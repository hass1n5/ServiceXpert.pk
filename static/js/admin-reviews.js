/* Reviews: create/edit modal, publish toggle, delete. */

(function () {
  "use strict";

  const modal = document.getElementById("reviewModal");
  const form = modal?.querySelector("form");

  function setField(name, value) {
    const el = form?.querySelector(`[name="${name}"]`);
    if (!el) return;
    if (el.type === "checkbox") el.checked = Boolean(value);
    else el.value = value ?? "";
  }

  function openReview(data) {
    if (!form) return;
    form.reset();

    const isNew = !data;
    document.getElementById("reviewTitle").textContent = isNew
      ? "Naya review"
      : `Edit: ${data.name}`;

    setField("id", isNew ? "" : data.id);
    setField("name", isNew ? "" : data.name);
    setField("city", isNew ? "" : data.city);
    setField("service", isNew ? "" : data.service);
    setField("rating", isNew ? 5 : data.rating);
    setField("body", isNew ? "" : data.body);
    setField("is_published", isNew ? true : data.is_published);

    Admin.openModal(modal);
  }

  document.querySelectorAll("[data-new-review]").forEach((button) => {
    button.addEventListener("click", () => openReview(null));
  });

  document.querySelectorAll("[data-edit-review]").forEach((button) => {
    button.addEventListener("click", () => {
      openReview(JSON.parse(button.closest("tr").dataset.review));
    });
  });

  document.querySelectorAll("[data-toggle-review]").forEach((box) => {
    box.addEventListener("change", () => {
      Admin.run(() =>
        Admin.api(`/api/reviews/${box.dataset.toggleReview}`, {
          method: "PATCH",
          body: JSON.stringify({ is_published: box.checked }),
        })
      ).catch(() => {
        box.checked = !box.checked;
      });
    });
  });

  document.querySelectorAll("[data-delete-review]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!confirm("Yeh review delete kar dein?")) return;
      Admin.run(
        () => Admin.api(`/api/reviews/${button.dataset.deleteReview}`, { method: "DELETE" }),
        { reload: true }
      ).catch(() => {});
    });
  });
})();
