// Ganesh DevOps Project 2 - Frontend Client Interaction

document.addEventListener("DOMContentLoaded", () => {
    const createForm = document.getElementById("createItemForm");
    if (createForm) {
        createForm.addEventListener("submit", handleCreateItem);
    }
});

async function handleCreateItem(e) {
    e.preventDefault();
    const titleInput = document.getElementById("itemTitle");
    const categoryInput = document.getElementById("itemCategory");
    const priorityInput = document.getElementById("itemPriority");
    const statusInput = document.getElementById("itemStatus");
    const descInput = document.getElementById("itemDesc");
    const submitBtn = document.getElementById("submitBtn");

    const payload = {
        title: titleInput.value.trim(),
        category: categoryInput.value,
        priority: priorityInput.value,
        status: statusInput.value,
        description: descInput.value.trim()
    };

    if (!payload.title) {
        alert("Please enter a valid task title.");
        return;
    }

    try {
        submitBtn.disabled = true;
        submitBtn.innerText = "Saving to API...";

        const response = await fetch("/api/items", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Failed to create item");
        }

        const newItem = await response.json();
        appendItemToTable(newItem);
        createFormReset();
        updateItemCount(1);
    } catch (err) {
        alert("Error creating item: " + err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "+ Add Item to API";
    }
}

function appendItemToTable(item) {
    const tbody = document.getElementById("itemsTableBody");
    if (!tbody) return;

    let priorityClass = "priority-normal";
    if (item.priority === "Critical") priorityClass = "priority-critical";
    else if (item.priority === "High") priorityClass = "priority-high";

    let statusBadge = `<span class="status-badge status-pending">⏳ ${item.status}</span>`;
    if (item.status === "Completed") {
        statusBadge = `<span class="status-badge status-completed">✓ ${item.status}</span>`;
    } else if (item.status === "In Progress") {
        statusBadge = `<span class="status-badge status-progress">⚡ ${item.status}</span>`;
    }

    const descHtml = item.description ? `<div class="item-desc-text">${escapeHtml(item.description)}</div>` : "";

    const tr = document.createElement("tr");
    tr.id = `row-${item.id}`;
    tr.innerHTML = `
        <td class="task-id">#${item.id}</td>
        <td class="task-title">
            <strong>${escapeHtml(item.title)}</strong>
            ${descHtml}
        </td>
        <td><span class="category-pill">${escapeHtml(item.category)}</span></td>
        <td><span class="priority-pill ${priorityClass}">${escapeHtml(item.priority)}</span></td>
        <td>${statusBadge}</td>
        <td class="task-time">${item.created_at}</td>
        <td>
            <button class="btn-delete" onclick="deleteItem(${item.id})">Delete</button>
        </td>
    `;
    tbody.prepend(tr);
}

async function deleteItem(itemId) {
    if (!confirm(`Are you sure you want to delete task #${itemId}?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/items/${itemId}`, {
            method: "DELETE"
        });

        if (response.status === 204 || response.ok) {
            const row = document.getElementById(`row-${itemId}`);
            if (row) {
                row.remove();
                updateItemCount(-1);
            }
        } else {
            alert("Could not delete item from backend.");
        }
    } catch (err) {
        alert("Delete failed: " + err.message);
    }
}

async function loadItems() {
    try {
        const response = await fetch("/api/items");
        if (response.ok) {
            const items = await response.json();
            const tbody = document.getElementById("itemsTableBody");
            tbody.innerHTML = "";
            items.forEach(item => appendItemToTable(item));
            const countDisplay = document.getElementById("itemCountDisplay");
            if (countDisplay) {
                countDisplay.innerText = `${items.length} Tasks`;
            }
        }
    } catch (err) {
        console.error("Error reloading items:", err);
    }
}

function updateItemCount(diff) {
    const countDisplay = document.getElementById("itemCountDisplay");
    if (!countDisplay) return;
    const current = parseInt(countDisplay.innerText) || 0;
    const updated = Math.max(0, current + diff);
    countDisplay.innerText = `${updated} Tasks`;
}

function createFormReset() {
    document.getElementById("itemTitle").value = "";
    document.getElementById("itemDesc").value = "";
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
