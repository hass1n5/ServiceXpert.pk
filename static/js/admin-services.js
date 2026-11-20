/* Services: create/edit modals, live toggles, delete. */

(function () {
  "use strict";

  const serviceModal = document.getElementById("serviceModal");
  const categoryModal = document.getElementById("categoryModal");
  const serviceForm = serviceModal?.querySelector("form");
  const categoryForm = categoryModal?.querySelector("form");
  const preview = document.getElementById("servicePreview");

  function setField(form, name, value) {
    const el = form.querySelector(`[name="${name}"]`);
    if (!el) return;
    if (el.type === "checkbox") el.checked = Boolean(value);
    else el.value = value ?? "";
  }

  /* ---------------------------------------------------------- services */

  function openService(data) {
    if (!serviceForm) return;
    serviceForm.reset();

    const isNew = !data;
    document.getElementById("serviceTitle").textContent = isNew
      ? "Nayi service"
      : `Edit: ${data.name}`;

    setField(serviceForm, "id", isNew ? "" : data.id);
    setField(serviceForm, "name", isNew ? "" : data.name);
    setField(serviceForm, "slug", isNew ? "" : data.slug);
    setField(serviceForm, "category_id", isNew ? "" : data.category_id);
    setField(serviceForm, "summary", isNew ? "" : data.summary);
    setField(serviceForm, "description", isNew ? "" : data.description);
    setField(serviceForm, "includes", isNew ? "" : data.includes);
    setField(serviceForm, "price_from", isNew ? "" : data.price_from);
    setField(serviceForm, "old_price", isNew ? "" : data.old_price);
    setField(serviceForm, "duration", isNew ? "" : data.duration);
    setField(serviceForm, "icon", isNew ? "sparkle" : data.icon);
    setField(serviceForm, "sort_order", isNew ? 0 : data.sort_order);
    setField(serviceForm, "is_active", isNew ? true : data.is_active);
    setField(serviceForm, "is_featured", isNew ? false : data.is_featured);

    if (preview) {
      const img = preview.querySelector("img");
      if (!isNew && data.image) {
        img.src = `/uploads/${data.image}`;
        preview.hidden = false;
      } else {
        preview.hidden = true;
      }
    }

    Admin.openModal(serviceModal);
  }

  document.querySelectorAll("[data-new-service]").forEach((button) => {
    button.addEventListener("click", () => openService(null));
  });

  document.querySelectorAll("[data-edit-service]").forEach((button) => {
    button.addEventListener("click", () => {
      openService(JSON.parse(button.closest("tr").dataset.service));
    });
  });

  document.querySelectorAll("[data-toggle-active]").forEach((box) => {
    box.addEventListener("change", () => {
      Admin.run(() =>
        Admin.api(`/api/services/${box.dataset.toggleActive}`, {
          method: "PATCH",
          body: JSON.stringify({ is_active: box.checked }),
        })
      ).catch(() => {
        box.checked = !box.checked;
      });
    });
  });

  document.querySelectorAll("[data-toggle-featured]").forEach((box) => {
    box.addEventListener("change", () => {
      Admin.run(() =>
        Admin.api(`/api/services/${box.dataset.toggleFeatured}`, {
          method: "PATCH",
          body: JSON.stringify({ is_featured: box.checked }),
        })
      ).catch(() => {
        box.checked = !box.checked;
      });
    });
  });

  document.querySelectorAll("[data-delete-service]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!confirm("Yeh service delete kar dein?")) return;
      Admin.run(
        () => Admin.api(`/api/services/${button.dataset.deleteService}`, { method: "DELETE" }),
        { reload: true }
      ).catch(() => {});
    });
  });

  /* -------------------------------------------------------- categories */

  function openCategory(data) {
    if (!categoryForm) return;
    categoryForm.reset();

    const isNew = !data;
    document.getElementById("categoryTitle").textContent = isNew
      ? "Nayi category"
      : `Edit: ${data.name}`;

    setField(categoryForm, "id", isNew ? "" : data.id);
    setField(categoryForm, "name", isNew ? "" : data.name);
    setField(categoryForm, "slug", isNew ? "" : data.slug);
    setField(categoryForm, "tagline", isNew ? "" : data.tagline);
    setField(categoryForm, "description", isNew ? "" : data.description);
    setField(categoryForm, "accent", isNew ? "green" : data.accent);
    setField(categoryForm, "sort_order", isNew ? 0 : data.sort_order);

    Admin.openModal(categoryModal);
  }

  document.querySelectorAll("[data-new-category]").forEach((button) => {
    button.addEventListener("click", () => openCategory(null));
  });

  document.querySelectorAll("[data-edit-category]").forEach((button) => {
    button.addEventListener("click", () => openCategory(JSON.parse(button.dataset.full)));
  });

  document.querySelectorAll("[data-delete-category]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!confirm("Category delete kar dein? Is mein koi service nahi honi chahiye.")) return;
      Admin.run(
        () => Admin.api(`/api/categories/${button.dataset.deleteCategory}`, { method: "DELETE" }),
        { reload: true }
      ).catch(() => {});
    });
  });
  /* --------------------------------------------------- duplicate a service */

  const duplicateForm = document.getElementById("duplicateForm");

  document.querySelectorAll("[data-duplicate-service]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!duplicateForm) return;
      const row = button.closest("tr");
      const name = row ? JSON.parse(row.dataset.service).name : "is service";
      if (!confirm(`"${name}" ki copy bana dein? Copy off rahegi jab tak aap edit na karein.`)) return;
      duplicateForm.action = `/admin/services/${button.dataset.duplicateService}/duplicate`;
      duplicateForm.submit();
    });
  });

  /* ------------------------------------------------------ search / filter */

  const search = document.getElementById("serviceSearch");
  const hits = document.getElementById("serviceHits");

  if (search) {
    const rows = Array.from(document.querySelectorAll("tr[data-service]"));

    const haystack = new Map(
      rows.map((row) => {
        const svc = JSON.parse(row.dataset.service);
        return [
          row,
          `${svc.name} ${svc.slug} ${svc.category || ""} ${svc.summary || ""}`.toLowerCase(),
        ];
      })
    );

    function filter() {
      const term = search.value.trim().toLowerCase();
      let matched = 0;

      rows.forEach((row) => {
        const show = !term || haystack.get(row).includes(term);
        row.hidden = !show;
        if (show) matched += 1;
      });

      /* A category with nothing left in it hides too, along with its
         "koi service nahi" placeholder row. */
      document.querySelectorAll("section.panel").forEach((panel) => {
        const own = panel.querySelectorAll("tr[data-service]");
        if (!own.length) return;
        const any = Array.from(own).some((row) => !row.hidden);
        panel.hidden = Boolean(term) && !any;
        const blank = panel.querySelector("td.empty");
        if (blank) blank.closest("tr").hidden = Boolean(term);
      });

      if (hits) {
        hits.hidden = !term;
        hits.textContent = `${matched} mili`;
      }
    }

    search.addEventListener("input", filter);
    search.addEventListener("search", filter);

    document.addEventListener("keydown", (event) => {
      if (event.key === "/" && document.activeElement.tagName !== "INPUT" &&
          document.activeElement.tagName !== "TEXTAREA") {
        event.preventDefault();
        search.focus();
      }
    });
  }
})();
