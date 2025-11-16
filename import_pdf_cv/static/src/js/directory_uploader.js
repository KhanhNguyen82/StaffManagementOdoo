/** @odoo-module **/

import { Component, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class DirectoryUploader extends Component {
    static template = "import_pdf_cv.DirectoryUploader";

    setup() {
        this.fileInput = useRef("fileInput");
        this.warning = useRef("warning");
        this.action = useService("action");
        this.notification = useService("notification");

        // trạng thái tiến trình
        this.state = useState({
            total: 0,
            done: 0,
            inProgress: false,
        });
    }

    async onFilesSelected(ev) {
        const files = ev.target.files;
        if (!files.length) return;

        this.warning.el.classList.remove("d-none");
        this.state.inProgress = true;
        this.state.total = files.length;
        this.state.done = 0;

        const concurrency = 3; // số request song song tối đa
        const fileList = Array.from(files).filter(f => f.name.toLowerCase().endsWith(".pdf"));

        // Worker: gửi lần lượt từng file
        let index = 0;
        const worker = async () => {
            while (index < fileList.length) {
                const i = index++;
                const file = fileList[i];

                const formData = new FormData();
                formData.append("files[]", file, file.webkitRelativePath || file.name);

                try {
                    await fetch("/upload_directory", {
                        method: "POST",
                        body: formData,
                    });
                    this.state.done += 1;
                } catch (err) {
                    console.error("Lỗi upload:", file.name, err);
                    this.notification.add(`Lỗi upload ${file.name}`, { type: "danger" });
                }
            }
        };

        // Chạy 3 worker song song
        await Promise.all([...Array(concurrency)].map(worker));

        this.state.inProgress = false;

        this.notification.add(
            `All CV PDF files have been uploaded and queued for processing! ${this.state.done}/${this.state.total} file. Estimated time: ${this.state.total*2} min.`,
            { type: "success", sticky: true }
        );
        this.warning.el.classList.add("d-none");
        this.action.doAction("import_pdf_cv.action_ir_attachment_process_pending_attachments");
    }

    // Helper hiển thị %
    get progressPercent() {
        if (!this.state.total) return 0;
        return Math.round((this.state.done / this.state.total) * 100);
    }
}

registry.category("actions").add("import_pdf_cv_directory_uploader", DirectoryUploader);
