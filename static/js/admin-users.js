/* Clients and admin users: activate/deactivate, delete, create admin. */

(function () {
  "use strict";

  document.querySelectorAll("[data-toggle-user]").forEach((button) => {
    button.addEventListener("click", () => {
      const makeActive = button.dataset.active !== "true";
      Admin.run(
        () =>
          Admin.api(`/api/users/${button.dataset.toggleUser}`, {
            method: "PATCH",
            body: JSON.stringify({ active: makeActive }),
          }),
        { reload: true }
      ).catch(() => {});
    });
  });

  document.querySelectorAll("[data-delete-user]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!confirm("Yeh account delete ho jayega. Bookings mehfooz rahengi. Jari rakhein?"))
        return;
      Admin.run(
        () => Admin.api(`/api/users/${button.dataset.deleteUser}`, { method: "DELETE" }),
        { reload: true }
      ).catch(() => {});
    });
  });

  /* -------------------------------------------------- new admin account */

  const modal = document.getElementById("adminModal");
  const form = document.getElementById("adminForm");

  document.querySelectorAll("[data-new-admin]").forEach((button) => {
    button.addEventListener("click", () => {
      form?.reset();
      Admin.showError(modal, "");
      Admin.openModal(modal);
    });
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {};
    form.querySelectorAll("input").forEach((el) => {
      if (el.name) payload[el.name] = el.value.trim();
    });
    payload.role = "admin";

    try {
      await Admin.run(
        () => Admin.api("/api/users", { method: "POST", body: JSON.stringify(payload) }),
        { reload: true }
      );
      Admin.closeModal(modal);
    } catch (error) {
      Admin.showError(modal, error.message);
    }
  });
})();
