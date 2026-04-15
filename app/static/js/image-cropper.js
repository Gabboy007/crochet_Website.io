(function () {
  function loadImage(file) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = reject;
      image.src = URL.createObjectURL(file);
    });
  }

  function loadImageFromUrl(url) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = reject;
      image.src = url;
    });
  }

  function setInputFiles(input, items) {
    const dataTransfer = new DataTransfer();
    items.forEach((item) => dataTransfer.items.add(item.file));
    input.files = dataTransfer.files;
  }

  function renderCrop(canvas, item) {
    const context = canvas.getContext("2d");
    const size = canvas.width;
    context.clearRect(0, 0, size, size);
    context.fillStyle = "#fff8fb";
    context.fillRect(0, 0, size, size);

    const image = item.image;
    const baseScale = Math.max(size / image.width, size / image.height);
    const scale = baseScale * item.zoom;
    const width = image.width * scale;
    const height = image.height * scale;
    const x = (size - width) / 2 + item.offsetX;
    const y = (size - height) / 2 + item.offsetY;

    context.drawImage(image, x, y, width, height);
  }

  function cropToFile(canvas, originalFile) {
    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        const cleanName = originalFile.name.replace(/\.[^.]+$/, "");
        resolve(new File([blob], `${cleanName}-showcase.jpg`, { type: "image/jpeg" }));
      }, "image/jpeg", 0.9);
    });
  }

  function ensureModal() {
    let modal = document.getElementById("imageCropModal");
    if (modal) return modal;

    modal = document.createElement("div");
    modal.id = "imageCropModal";
    modal.className = "image-crop-modal";
    modal.innerHTML = `
      <div class="image-crop-backdrop" data-crop-cancel></div>
      <section class="image-crop-panel" role="dialog" aria-modal="true" aria-label="Edit product picture">
        <div class="image-crop-head">
          <div>
            <p class="admin-eyebrow">Edit Picture</p>
            <h2>Adjust showcase view</h2>
          </div>
          <button type="button" class="close-btn" data-crop-cancel aria-label="Close image editor">X</button>
        </div>
        <div class="image-crop-workspace">
          <canvas class="image-crop-canvas" width="900" height="900"></canvas>
          <div class="image-position-controls" aria-label="Position picture">
            <span>Position</span>
            <button type="button" class="mini-action" data-crop-move="up" aria-label="Move picture up">Up</button>
            <div class="image-position-row">
              <button type="button" class="mini-action" data-crop-move="left" aria-label="Move picture left">Left</button>
              <button type="button" class="mini-action" data-crop-move="right" aria-label="Move picture right">Right</button>
            </div>
            <button type="button" class="mini-action" data-crop-move="down" aria-label="Move picture down">Down</button>
          </div>
        </div>
        <p class="form-hint">Drag the picture or use the position buttons. Zoom in or out before saving.</p>
        <label class="image-crop-zoom">
          Zoom
          <div class="image-crop-zoom-controls">
            <button type="button" class="mini-action" data-crop-zoom-out aria-label="Zoom out">-</button>
            <input type="range" min="1" max="3" step="0.01" value="1" data-crop-zoom>
            <button type="button" class="mini-action" data-crop-zoom-in aria-label="Zoom in">+</button>
          </div>
        </label>
        <div class="form-actions">
          <button type="button" class="btn btn-primary" data-crop-save>Use This View</button>
          <button type="button" class="btn btn-secondary" data-crop-reset>Reset</button>
        </div>
      </section>
    `;
    document.body.appendChild(modal);
    return modal;
  }

  function createCropEditor({ onSave }) {
    const modal = ensureModal();
    const canvas = modal.querySelector(".image-crop-canvas");
    const zoomInput = modal.querySelector("[data-crop-zoom]");
    const zoomInButton = modal.querySelector("[data-crop-zoom-in]");
    const zoomOutButton = modal.querySelector("[data-crop-zoom-out]");
    let activeItem = null;
    let dragging = false;
    let lastX = 0;
    let lastY = 0;

    function closeEditor() {
      modal.classList.remove("active");
      document.body.style.overflow = "";
      activeItem = null;
    }

    function openEditor(item) {
      activeItem = item;
      zoomInput.value = activeItem.zoom;
      renderCrop(canvas, activeItem);
      modal.classList.add("active");
      document.body.style.overflow = "hidden";
    }

    function updateZoom(value) {
      if (!activeItem) return;
      const min = Number(zoomInput.min);
      const max = Number(zoomInput.max);
      const nextZoom = Math.min(max, Math.max(min, value));
      activeItem.zoom = nextZoom;
      zoomInput.value = nextZoom;
      renderCrop(canvas, activeItem);
    }

    function moveImage(direction) {
      if (!activeItem) return;
      const step = canvas.width * 0.035;

      if (direction === "up") activeItem.offsetY -= step;
      if (direction === "down") activeItem.offsetY += step;
      if (direction === "left") activeItem.offsetX -= step;
      if (direction === "right") activeItem.offsetX += step;

      renderCrop(canvas, activeItem);
    }

    canvas.addEventListener("pointerdown", (event) => {
      if (!activeItem) return;
      event.preventDefault();
      dragging = true;
      lastX = event.clientX;
      lastY = event.clientY;
      canvas.setPointerCapture(event.pointerId);
    });

    canvas.addEventListener("pointermove", (event) => {
      if (!dragging || !activeItem) return;
      event.preventDefault();
      activeItem.offsetX += event.clientX - lastX;
      activeItem.offsetY += event.clientY - lastY;
      lastX = event.clientX;
      lastY = event.clientY;
      renderCrop(canvas, activeItem);
    });

    canvas.addEventListener("pointerup", () => {
      dragging = false;
    });

    canvas.addEventListener("pointercancel", () => {
      dragging = false;
    });

    canvas.addEventListener("lostpointercapture", () => {
      dragging = false;
    });

    zoomInput.addEventListener("input", () => {
      updateZoom(Number(zoomInput.value));
    });

    zoomInButton.addEventListener("click", () => {
      updateZoom(Number(zoomInput.value) + 0.1);
    });

    zoomOutButton.addEventListener("click", () => {
      updateZoom(Number(zoomInput.value) - 0.1);
    });

    modal.querySelectorAll("[data-crop-move]").forEach((button) => {
      button.addEventListener("click", () => {
        moveImage(button.dataset.cropMove);
      });
    });

    canvas.addEventListener("wheel", (event) => {
      if (!activeItem) return;
      event.preventDefault();
      updateZoom(Number(zoomInput.value) + (event.deltaY < 0 ? 0.08 : -0.08));
    }, { passive: false });

    modal.querySelector("[data-crop-reset]").addEventListener("click", () => {
      if (!activeItem) return;
      activeItem.zoom = 1;
      activeItem.offsetX = 0;
      activeItem.offsetY = 0;
      zoomInput.value = 1;
      renderCrop(canvas, activeItem);
    });

    modal.querySelector("[data-crop-save]").addEventListener("click", async () => {
      if (!activeItem) return;
      renderCrop(canvas, activeItem);
      const croppedFile = await cropToFile(canvas, activeItem.originalFile);
      await onSave(croppedFile, activeItem);
      closeEditor();
    });

    modal.querySelectorAll("[data-crop-cancel]").forEach((button) => {
      button.addEventListener("click", closeEditor);
    });

    return { openEditor };
  }

  function setupImageCropper({ inputId, previewId, maxFiles }) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;

    let items = [];
    let activeIndex = -1;
    const editor = createCropEditor({
      onSave: async (croppedFile, activeItem) => {
        activeItem.file = croppedFile;
        activeItem.previewUrl = URL.createObjectURL(croppedFile);
        items[activeIndex] = activeItem;
        setInputFiles(input, items);
        renderPreview();
      },
    });

    function renderPreview() {
      preview.innerHTML = "";
      items.forEach((item, index) => {
        const card = document.createElement("div");
        card.className = "preview-card editable-preview-card";
        card.innerHTML = `
          <img src="${item.previewUrl}" alt="${item.file.name}">
          <p>${item.file.name}</p>
          <div class="preview-actions">
            <button type="button" class="mini-action" data-edit="${index}">Edit View</button>
            <button type="button" class="mini-action remove-preview" data-remove="${index}">Remove</button>
          </div>
        `;
        preview.appendChild(card);
      });

      preview.querySelectorAll("[data-edit]").forEach((button) => {
        button.addEventListener("click", () => {
          activeIndex = Number(button.dataset.edit);
          editor.openEditor(items[activeIndex]);
        });
      });

      preview.querySelectorAll("[data-remove]").forEach((button) => {
        button.addEventListener("click", () => {
          items.splice(Number(button.dataset.remove), 1);
          setInputFiles(input, items);
          renderPreview();
        });
      });
    }

    input.addEventListener("change", async function () {
      const selectedFiles = Array.from(this.files).filter((file) => file.type.startsWith("image/"));

      if (selectedFiles.length > maxFiles) {
        alert(`You can upload up to ${maxFiles} image(s).`);
        this.value = "";
        items = [];
        preview.innerHTML = "";
        return;
      }

      items = await Promise.all(selectedFiles.map(async (file) => {
        const image = await loadImage(file);
        return {
          originalFile: file,
          file,
          image,
          zoom: 1,
          offsetX: 0,
          offsetY: 0,
          previewUrl: URL.createObjectURL(file),
        };
      }));

      setInputFiles(input, items);
      renderPreview();
    });
  }

  function setupExistingImageEditors() {
    const buttons = document.querySelectorAll("[data-existing-image-edit]");
    if (!buttons.length) return;

    const editor = createCropEditor({
      onSave: async (croppedFile, activeItem) => {
        const formData = new FormData();
        formData.append("image", croppedFile);

        const response = await fetch(activeItem.saveUrl, {
          method: "POST",
          body: formData,
          credentials: "same-origin",
        });

        if (!response.ok) {
          alert("Could not save this picture edit yet.");
          return;
        }

        window.location.reload();
      },
    });

    buttons.forEach((button) => {
      button.addEventListener("click", async () => {
        button.disabled = true;
        button.textContent = "Loading...";

        try {
          const image = await loadImageFromUrl(button.dataset.imageSrc);
          editor.openEditor({
            originalFile: new File([], "edited-product-image.jpg", { type: "image/jpeg" }),
            image,
            zoom: 1,
            offsetX: 0,
            offsetY: 0,
            saveUrl: button.dataset.saveUrl,
          });
        } catch (error) {
          alert("Could not open this image for editing.");
        } finally {
          button.disabled = false;
          button.textContent = "Edit View";
        }
      });
    });
  }

  window.setupImageCropper = setupImageCropper;
  window.setupExistingImageEditors = setupExistingImageEditors;
})();
