<template>
  <div class="clearfix">
    <a-upload :file-list="fileList" :before-upload="beforeUpload" :remove="handleRemove">
      <a-button>
        <!-- <upload-outlined></upload-outlined> -->
        选择待检测源码文件
      </a-button>
    </a-upload>
    <a-button
      type="primary"
      :disabled="fileList.length === 0"
      :loading="uploading"
      style="margin-top: 16px"
      @click="handleUpload"
    >
      {{ uploading ? '正在上传并分析漏洞' : '上传' }}
    </a-button>
  </div>
</template>

<script>
import request from 'umi-request';
import { UploadOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { defineComponent, ref } from 'vue';

export default defineComponent({
  components: {
    UploadOutlined,
  },
  data () {
    return {
      fileList: [],
      uploading: false,
    }
  },
  methods: {
    // 文件移除
    handleRemove (file) {
      const index = this.fileList.indexOf(file)
      const newFileList = this.fileList.slice()
      newFileList.splice(index, 1)
      this.fileList = newFileList
    },
    beforeUpload (file) {
      this.fileList = [...this.fileList, file]
      return false // false 表示不立即发送
    },
    async setAndJumpToLocation(response_json) {
      console.log(response_json)
    },
    // 上传文件点击确认
    handleUpload () {
      const { fileList } = this
      const formData = new FormData()
      fileList.forEach((file) => {
        formData.append('file', file)
        // console.log(formData.get('file'))
      })
      this.uploading = true

      // You can use any AJAX library you like
      request.post('http://127.0.0.1:5000/upload', {
        data: formData,
      })
        .then((response) => {
          fileList.value = [];
          this.uploading = false;
          message.success({
            content: '上传成功',
            style: {
              marginTop: '20vh',
            },
          });
          this.setAndJumpToLocation(response);
        })
        .catch((error) => {
          // console.log(error, error.response)
          this.uploading = false;
          var msg = '上传失败' + (error.response ? ": " + error.response.statusText : "");
          console.log(msg)
          message.error({
            content: msg,
            style: {
              marginTop: '20vh',
            },
          });
        });
    }
  }
})
</script>
