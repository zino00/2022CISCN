<template>
  <div class="clearfix">
    <a-upload-dragger :file-list="fileList" :before-upload="beforeUpload" :remove="handleRemove"
    >
      <p class="ant-upload-drag-icon">
        <inbox-outlined></inbox-outlined>
      </p>
      <p class="ant-upload-text">上传文件</p>
      <p class="ant-upload-hint">
        点击此处上传待检测的文件，若有多个文件请先压缩再上传
      </p>
    </a-upload-dragger>

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

<script lang="ts">
import request from 'umi-request';
import { UploadOutlined } from '@ant-design/icons-vue';
import { InboxOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { defineComponent, ref } from 'vue';
// import type { UploadChangeParam } from 'ant-design-vue';

export default defineComponent({
  components: {
    UploadOutlined, InboxOutlined
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

    async setAndJumpToLocation(res_arr) {
      // 清除原始数据
      this.$g.locatemenus.items = res_arr
      // console.log(this.$g.locatemenus.items)
      this.$router.push({ path:'/pages/detect'})
    },


    // 上传文件点击确认
    handleUpload () {
      const { fileList } = this
      const formData = new FormData()
      fileList.forEach((file) => {
        // console.log(file)
        formData.append('file', file)
        console.log(formData.get('file') == file)
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
            content: '分析完成',
            style: {
              marginTop: '20vh',
            },
          });
          if(response.result == undefined) {
              message.warn({
                content: "分析数据异常",
                style: {
                  marginTop: '20vh',
                },
            });
          }
          this.setAndJumpToLocation(response.result);
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
