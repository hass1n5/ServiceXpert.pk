/* Bookings: inline status change, detail modal, WhatsApp links, delete. */

(function () {
  "use strict";

  const modal = document.getElementById("bookingModal");
  const facts = document.getElementById("bookingFacts");
  const title = document.getElementById("bookingTitle");
  const statusInput = document.getElementById("b-status");
  const priceInput = document.getElementById("b-price");
  const noteInput = document.getElementById("b-note");

  let current = null;

  function row(label, value) {
    if (!value) return "";
    return `<div style="display:flex;gap:10px">
              <span style="color:var(--ink-faint);min-width:110px">${label}</span>
              <span>${String(value).replace(/</g, "&lt;")}</span>
            </div>`;
  }

  function openBooking(data) {
    current = data;
    title.textContent = `${data.reference} — ${data.service}`;

    facts.innerHTML =
      row("Naam", data.name) +
      row("Phone", data.phone) +
      row("Email", data.email) +
      row("Shehar", data.city) +
      row("Pata", data.address) +
      row("Pasandeeda din", data.preferred_date) +
      row("Aayi", data.created_at) +
      row("Tafseel", data.message);

    statusInput.value = data.status;
    priceInput.value = data.quoted_price || "";
    noteInput.value = data.admin_note || "";
    Admin.showError(modal, "");
    Admin.openModal(modal);
  }

  document.querySelectorAll("[data-open-booking]").forEach((button) => {
    button.addEventListener("click", () => {
      const row = button.closest("tr");
      openBooking(JSON.parse(row.dataset.booking));
    });
  });

  /* Inline status change straight from the table */
  document.querySelectorAll(".status-select[data-booking-id]").forEach((select) => {
    let previous = select.value;
    select.addEventListener("change", async () => {
      try {
        await Admin.run(() =>
          Admin.api(`/api/bookings/${select.dataset.bookingId}`, {
            method: "PATCH",
            body: JSON.stringify({ status: select.value }),
          })
        );
        previous = select.value;
      } catch (_) {
        select.value = previous;
      }
    });
  });

  document.querySelector("[data-save-booking]")?.addEventListener("click", async () => {
    if (!current) return;
    try {
      await Admin.run(() =>
        Admin.api(`/api/bookings/${current.id}`, {
          method: "PATCH",
          body: JSON.stringify({
            status: statusInput.value,
            quoted_price: priceInput.value === "" ? null : priceInput.value,
            admin_note: noteInput.value,
          }),
        })
      , { reload: true });
      Admin.closeModal(modal);
    } catch (error) {
      Admin.showError(modal, error.message);
    }
  });

  document.querySelector("[data-forward]")?.addEventListener("click", async () => {
    if (!current) return;
    try {
      const payload = await Admin.api(`/api/bookings/${current.id}/forward`);
      window.open(payload.url, "_blank", "noopener");
    } catch (error) {
      Admin.showError(modal, error.message);
    }
  });

  /* Message the customer directly */
  document.querySelectorAll("[data-wa-customer]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        const payload = await Admin.api(
          `/api/bookings/${button.dataset.waCustomer}/whatsapp`
        );
        window.open(payload.url, "_blank", "noopener");
      } catch (error) {
        Admin.toast(error.message, true);
      }
    });
  });

  document.querySelectorAll("[data-delete-booking]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!confirm("Yeh booking permanently delete ho jayegi. Jari rakhein?")) return;
      Admin.run(
        () =>
          Admin.api(`/api/bookings/${button.dataset.deleteBooking}`, { method: "DELETE" }),
        { reload: true }
      ).catch(() => {});
    });
  });
})();
