/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FileInput } from "@web/core/file_upload/file_input";

patch(FileInput.prototype, {
    setup() {
        this._super();
    },

    render() {
        const el = this._super();
        try {
            // Áp dụng cho wizard candidate.import.wizard_2
            if (this.props.resModel === "candidate.import.wizard_2") {
                el.setAttribute("accept", "application/pdf");
            }
        } catch (e) {
            console.warn("Patch FileInput accept error:", e);
        }
        return el;
    },
});
