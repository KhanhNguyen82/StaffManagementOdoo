/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";

patch(FormRenderer.prototype, {
    setup() {
        super.setup && super.setup();
        console.log(">>> FormRenderer patch loaded");

        // Đảm bảo chỉ bind 1 lần cho mỗi renderer
        if (this._pdfListenerBound) {
            return;
        }
        this._pdfListenerBound = true;

        // Delay một chút để DOM nút render xong
        setTimeout(() => {
            const btn = document.querySelector("button.o_import_pdf_upload");

            if (btn) {
                console.log(">>> Found Import PDF button:", btn);

                btn.addEventListener(
                    "click",
                    (ev) => {
                        console.log(">>> Patched click on Import PDF button");

                        // Ẩn nút Import
                        btn.classList.add("d-none");
                        btn.setAttribute("disabled", "true");
                        //const cancelBtn = document.querySelector('footer button[special="cancel"]');
                        //if (cancelBtn) cancelBtn.click();
                        // Hiện nút Ok mặc định
                        const okBtn = document.querySelector("button.o-default-button");
                        if (okBtn) {
                            okBtn.classList.remove("d-none");
                            okBtn.focus();
                            console.log(">>> Ok button is now visible");
                        } else {
                            console.warn(">>> Ok button not found");
                        };

                        const p_pro = document.querySelector("p#p-processing");
                        if (p_pro) {
                            p_pro.classList.remove("d-none");
                        };

                    },
                    true // capture để chắc chắn bắt được click
                );
            } else {
                console.warn(">>> Import PDF button not found at setup");
            };

        }, 500);
    },
});
