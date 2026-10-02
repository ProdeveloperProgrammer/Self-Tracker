/* Add / edit record popup shared by subpage.html and finance.html.
   Needs window.RECORDS (see includes/record_modal.html) and the popup markup. */
(function () {
    'use strict';
    var C = window.RECORDS || {};
    var $ = function (id) { return document.getElementById(id); };
    var pad = function (n) { return String(n).padStart(2, '0'); };

    function open() {
        $('modalOverlay').classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function clearFilePreviews() {
        document.querySelectorAll('.current-file-info').forEach(function (el) { el.remove(); });
    }

    // "10:40 p.m.", "10:40PM", "22:40", "10:40:00 a.m." -> "HH:MM"
    function toHHMM(raw) {
        var m = (raw || '').match(/(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)?/i);
        if (!m) return '';
        var h = parseInt(m[1], 10);
        var mer = m[4] ? m[4].toLowerCase().replace(/\./g, '') : null;
        if (mer === 'pm' && h !== 12) h += 12;
        else if (mer === 'am' && h === 12) h = 0;
        return pad(h) + ':' + m[2];
    }

    // ISO strings pass straight through; anything else ("Sept. 17, 2026") is parsed
    function toISODate(raw) {
        if (/^\d{4}-\d{2}-\d{2}/.test(raw)) return raw.slice(0, 10);
        var d = new Date(raw);
        return isNaN(d) ? '' : d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
    }

    function showFilePreview(input, raw) {
        var box = document.createElement('div');
        box.className = 'current-file-info';
        box.style.cssText = 'font-size: 0.82rem; margin-top: 6px; color: var(--text-secondary);';
        var link = document.createElement('a');
        link.href = C.mediaUrl + raw;
        link.target = '_blank';
        link.textContent = raw.split('/').pop();
        link.style.cssText = 'color: var(--accent-color); font-weight: 600; text-decoration: underline;';
        var hint = document.createElement('span');
        hint.style.opacity = '0.7';
        hint.textContent = ' (Upload a new file only to replace it)';
        box.append('\uD83D\uDCC1 Current File: ', link, hint);
        input.parentElement.appendChild(box);
    }

    // values[i] belongs to C.fieldNames[i]; matched by field NAME, never by input position
    function fill(form, values) {
        values.forEach(function (raw, i) {
            var input = form.elements[C.fieldNames[i]];
            if (!input) return;

            if (typeof RadioNodeList !== 'undefined' && input instanceof RadioNodeList) {
                input.value = raw;
            } else if (input.type === 'file') {
                input.value = '';
                input.removeAttribute('required');     // allow saving without re-uploading
                if (raw && raw !== 'None') showFilePreview(input, raw);
            } else if (input.type === 'checkbox') {
                input.checked = raw === 'True' || raw === 'true';
            } else if (input.type === 'date') {
                input.value = toISODate(raw);
            } else if (input.type === 'time') {
                input.value = toHHMM(raw);
            } else {
                input.value = raw === 'None' ? '' : raw;
            }
        });
    }

    window.openCreateModal = function () {
        var form = $('recordForm');
        form.action = C.createUrl;
        $('modalTitle').innerText = 'Add New Record';
        $('itemId').value = '';
        form.reset();
        clearFilePreviews();
        open();
    };

    window.openEditModalWithValues = function (id, name, values) {
        var form = $('recordForm');
        form.action = C.updateUrl.replace('999999', id);
        $('modalTitle').innerText = 'Edit Record - ' + name;
        $('itemId').value = id;
        clearFilePreviews();
        fill(form, values);
        open();
    };

    // subpage.html: read the values straight from the table row
    window.openEditModal = function (row, id, name) {
        var values = Array.prototype.map.call(
            row.querySelectorAll('td[data-cell-value]'),
            function (td) { return td.getAttribute('data-cell-value'); }
        );
        window.openEditModalWithValues(id, name, values);
    };

    window.closeModal = function () {
        $('modalOverlay').classList.remove('active');
        document.body.style.overflow = '';
    };

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') window.closeModal();
    });

    // Backend validation failed on POST -> reopen the popup with the errors
    if (C.showModal) {
        document.addEventListener('DOMContentLoaded', function () {
            var form = $('recordForm');
            if (C.editPk) {
                $('modalTitle').innerText = 'Edit Record - Errors Found';
                form.action = C.updateUrl.replace('999999', C.editPk);
                $('itemId').value = C.editPk;
            } else {
                $('modalTitle').innerText = 'Add New Record - Errors Found';
                form.action = C.createUrl;
                $('itemId').value = '';
            }
            open();
        });
    }
})();
