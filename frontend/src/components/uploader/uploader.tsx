import { defineComponent, ref } from 'vue'
import { message } from 'ant-design-vue';
import { UploadOutlined } from '@ant-design/icons-vue';

import type { UploadChangeParam } from 'ant-design-vue';

const Uploader=defineComponent({
    name: 'MiUploader',
    components: {
        UploadOutlined,
      },
      setup() {
        const handleChange = (info: UploadChangeParam) => {
          if (info.file.status !== 'uploading') {
            console.log(info.file, info.fileList);
          }
          if (info.file.status === 'done') {
            message.success(`${info.file.name} file uploaded successfully`);
          } else if (info.file.status === 'error') {
            message.error(`${info.file.name} file upload failed.`);
          }
        };
    
        const fileList = ref([]);
        return {
          fileList,
          headers: {
            authorization: 'authorization-text',
          },
          handleChange,
        };
      },
})

export default Uploader as typeof Uploader