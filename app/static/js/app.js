// SortableJS initialization and HTMX event handlers

document.addEventListener("DOMContentLoaded", function () {
    initSortable();
    initModal();
});

// Re-init after HTMX swaps
document.addEventListener("htmx:afterSwap", function () {
    initSortable();
});

function initSortable() {
    const favoritesGrid = document.getElementById("favorites-grid");
    if (favoritesGrid && !favoritesGrid._sortable) {
        favoritesGrid._sortable = new Sortable(favoritesGrid, {
            animation: 150,
            ghostClass: "sortable-ghost",
            dragClass: "sortable-drag",
            handle: ".house-tile",
            onEnd: function () {
                const ids = Array.from(favoritesGrid.children).map(
                    (el) => el.dataset.houseId
                );
                fetch("/houses/favorites/order", {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ordered_ids: ids }),
                });
            },
        });
    }
}

function initModal() {
    // Close modal on backdrop click
    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("modal-backdrop")) {
            closeModal();
        }
    });

    // Close modal on Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeModal();
        }
    });
}

function openModal() {
    const modal = document.getElementById("add-house-modal");
    if (modal) {
        modal.classList.remove("hidden");
    }
}

function closeModal() {
    const modal = document.getElementById("add-house-modal");
    if (modal) {
        modal.classList.add("hidden");
        // Reset form
        const form = modal.querySelector("form");
        if (form) form.reset();
    }
}

// Parse address from Zillow URL slug client-side
// e.g. /homedetails/141-Leigh-Rd-Cumberland-RI-02864/... -> "141 Leigh Rd, Cumberland, RI 02864"
function extractAddressFromZillowUrl(url) {
    const addressField = document.getElementById("address-field");
    if (!addressField) return;

    const match = url.match(/\/homedetails\/([^/]+)/);
    if (!match) return;

    let slug = match[1].replace(/-\d+_zpid$/, "");
    const parts = slug.split("-");

    if (
        parts.length >= 3 &&
        /^\d{5}$/.test(parts[parts.length - 1]) &&
        /^[A-Z]{2}$/i.test(parts[parts.length - 2])
    ) {
        const zipcode = parts[parts.length - 1];
        const state = parts[parts.length - 2].toUpperCase();
        const remaining = parts.slice(0, -2);

        const streetSuffixes = new Set([
            "rd", "st", "ave", "blvd", "dr", "ln", "ct", "pl", "way",
            "ter", "cir", "hwy", "pike", "run", "trail", "loop",
        ]);

        let boundary = remaining.length;
        for (let i = remaining.length - 1; i >= 0; i--) {
            if (streetSuffixes.has(remaining[i].toLowerCase())) {
                boundary = i + 1;
                break;
            }
        }

        const street = remaining
            .slice(0, boundary)
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
            .join(" ");
        const city = remaining
            .slice(boundary)
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
            .join(" ");

        addressField.value = city
            ? `${street}, ${city}, ${state} ${zipcode}`
            : `${street}, ${state} ${zipcode}`;
    }
}

// Close modal and reload only on true success (server sets X-House-Added header)
document.addEventListener("htmx:afterRequest", function (e) {
    if (e.detail.elt && e.detail.elt.id === "add-house-form") {
        if (e.detail.successful && e.detail.xhr.getResponseHeader("X-House-Added") === "true") {
            setTimeout(function () {
                closeModal();
                window.location.reload();
            }, 500);
        }
    }
});

function openEditModal(houseId) {
    const modal = document.getElementById("edit-house-modal");
    const container = document.getElementById("edit-form-container");
    if (!modal || !container) return;

    fetch("/houses/" + houseId + "/edit")
        .then((res) => res.text())
        .then((html) => {
            const form = document.createElement("form");
            form.id = "edit-house-form";
            form.innerHTML = html;
            form.addEventListener("submit", function (e) {
                e.preventDefault();
                submitEditForm(houseId, form);
            });
            container.innerHTML = "";
            container.appendChild(form);
            modal.classList.remove("hidden");
        });
}

function submitEditForm(houseId, form) {
    const errorEl = form.querySelector("#edit-validation-error");
    const address = form.querySelector("[name=address]").value.trim();
    if (!address) {
        errorEl.textContent = "Address is required.";
        errorEl.classList.remove("hidden");
        return;
    }
    errorEl.classList.add("hidden");

    fetch("/houses/" + houseId, {
        method: "PATCH",
        body: new FormData(form),
    }).then((res) => {
        if (res.status === 204) {
            closeEditModal();
            window.location.reload();
        } else {
            errorEl.textContent = "Failed to save. Please try again.";
            errorEl.classList.remove("hidden");
        }
    });
}

function closeEditModal() {
    const modal = document.getElementById("edit-house-modal");
    if (modal) {
        modal.classList.add("hidden");
        const container = document.getElementById("edit-form-container");
        if (container) container.innerHTML = "";
    }
}

