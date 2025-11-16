/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardActionService } from "@web/webclient/actions/action_service";

function choosePdfFile(env, action) {
    // Tạo input type="file"
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/pdf";
    input.multiple = true;

    input.addEventListener("change", async (ev) => {
        const files = ev.target.files;
        for (const file of files) {
            const base64Data = await toBase64(file);

            // Update field attachment_ids với command [0,0,values]
            env.model.root.record.update({
                attachment_ids: [
                    [0, 0, {
                        name: file.name,
                        datas: base64Data.split(",")[1], // bỏ phần "data:application/pdf;base64,"
                        res_model: "candidate.import.wizard",
                        mimetype: "application/pdf",
                    }]
                ]
            });
        }
    });

    input.click();
    return Promise.resolve(); // tránh lỗi doActionButton
}

function toBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
    });
}

registry.category("actions").add("choose_pdf_file", choosePdfFile);
