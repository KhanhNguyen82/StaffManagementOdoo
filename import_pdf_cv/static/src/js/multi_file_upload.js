/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class MultiFileUpload extends Component {
    setup() {
        this.fileInput = useRef("fileInput");
        this.rpc = useService("rpc");
    }

    async onFileChange(ev) {
        const files = ev.target.files;
        if (!files.length) {
            return;
        }

        // Lấy res_model và res_id của record hiện tại
        const resModel = this.props.record.model.root.resModel;
        const resId = this.props.record.model.root.resId;

        if (!resId) {
            alert("Vui lòng lưu record trước khi upload file!");
            return;
        }

        // Chuẩn bị dữ liệu để gửi qua controller
        const formData = new FormData();
        for (let f of files) {
            formData.append("files[]", f);
        }
        formData.append("res_model", resModel);
        formData.append("res_id", resId);

        try {
            const response = await fetch("/multi_upload/upload", {
                method: "POST",
                body: formData,
            });
            const result = await response.json();

            if (result.status === "success") {
                // Refresh lại record để hiển thị file mới
                this.props.record.model.root.load();
            } else {
                alert("Upload thất bại, vui lòng thử lại!");
            }
        } catch (err) {
            console.error("Upload error:", err);
            alert("Có lỗi khi upload file!");
        }
    }

    onClick() {
        this.fileInput.el.click();
    }
}

MultiFileUpload.template = "multi_file_upload.MultiFileUpload";

// Đăng ký widget field mới
registry.category("fields").add("multi_file_upload", MultiFileUpload);
