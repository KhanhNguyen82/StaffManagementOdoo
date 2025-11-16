/** @odoo-module **/

import { Component, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class DirectoryUploader extends Component {
    static template = "import_pdf_cv.DirectoryUploader";

    setup() {
        this.fileInput = useRef("fileInput");
        this.warning = useRef("warning");
        this.action = useService("action");
        this.notification = useService("notification");
    }

    async onFilesSelected(ev) {
        const files = ev.target.files;
        if (!files.length) {
            return;
        }
        //const notification_uploading = this.notification.add("Uploading", { type: "warning" });
        //setTimeout(notification_uploading, 30000);

        this.warning.el.classList.remove("d-none");

        const formData = new FormData();
        for (let file of files) {
        if (file.name.toLowerCase().endsWith(".pdf")) {
            formData.append("files[]", file, file.webkitRelativePath || file.name);
            console.log("File PDF:", file.name, "Path:", file.webkitRelativePath);
        } else {
            console.log("Bỏ qua file không phải PDF:", file.name);
        }
        }

        // Gửi về controller
        const response = await fetch("/upload_directory", {
            method: "POST",
            body: formData,
        });
        const result = await response.json();

        if (result.status === "OK")  {

            this.notification.add(`All CV PDF files have been uploaded and queued for processing! (Estimated: ${result.time} min.)`,
                { type: "success", sticky: true });

            this.action.doAction("import_pdf_cv.action_ir_attachment_process_pending_attachments");
        } else {
            this.notification.add("Upload failure.", { type: "danger" });
            this.warning.el.classList.add("d-none");
        }
    }
}

registry.category("actions").add("import_pdf_cv_directory_uploader", DirectoryUploader);
