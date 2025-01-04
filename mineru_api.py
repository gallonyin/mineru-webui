import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import asyncio
import uuid
from typing import Dict
from concurrent.futures import ThreadPoolExecutor

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

# FastAPI 应用
app = FastAPI()
# 创建线程池
executor = ThreadPoolExecutor(max_workers=3)  # 可以根据需要调整worker数量

# 使用内存字典存储任务状态
TASK_STATUS: Dict[str, Dict] = {}

# 将同步的PDF处理函数包装成异步
async def process_pdf(pdf_path: str, output_dir: str):
    try:
        # 将耗时的PDF处理操作放在线程池中执行
        def process_pdf_sync():
            # 准备输出目录
            local_image_dir = os.path.join(output_dir, "images")
            local_md_dir = output_dir
            os.makedirs(local_image_dir, exist_ok=True)
            
            image_dir = str(os.path.basename(local_image_dir))
            image_writer = FileBasedDataWriter(local_image_dir)
            md_writer = FileBasedDataWriter(local_md_dir)
            
            # 读取PDF
            reader = FileBasedDataReader("")
            pdf_bytes = reader.read(pdf_path)
            name_without_suff = os.path.basename(pdf_path).split(".")[0]

            # 处理PDF
            ds = PymuDocDataset(pdf_bytes)
            
            if ds.classify() == SupportedPdfParseMethod.OCR:
                infer_result = ds.apply(doc_analyze, ocr=True)
                pipe_result = infer_result.pipe_ocr_mode(image_writer)
            else:
                infer_result = ds.apply(doc_analyze, ocr=False)
                pipe_result = infer_result.pipe_txt_mode(image_writer)

            # 生成输出文件
            output_files = {
                "model_pdf": os.path.join(local_md_dir, f"{name_without_suff}_model.pdf"),
                "layout_pdf": os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"),
                "spans_pdf": os.path.join(local_md_dir, f"{name_without_suff}_spans.pdf"),
                "markdown": os.path.join(local_md_dir, f"{name_without_suff}.md"),
                "content_list": os.path.join(local_md_dir, f"{name_without_suff}_content_list.json")
            }

            infer_result.draw_model(output_files["model_pdf"])
            pipe_result.draw_layout(output_files["layout_pdf"])
            pipe_result.draw_span(output_files["spans_pdf"])
            pipe_result.dump_md(md_writer, f"{name_without_suff}.md", image_dir)
            pipe_result.dump_content_list(md_writer, f"{name_without_suff}_content_list.json", image_dir)

            return {"status": "completed", "output_files": output_files}

        # 在线程池中执行同步操作
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, process_pdf_sync)
        return result
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@app.post("/upload")
async def upload_pdf(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只接受PDF文件")
    
    try:
        # 创建临时文件保存上传的PDF
        temp_dir = tempfile.mkdtemp()
        temp_pdf = os.path.join(temp_dir, file.filename)
        
        # 保存上传的文件
        content = await file.read()
        with open(temp_pdf, "wb") as buffer:
            buffer.write(content)
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 启动异步任务
        asyncio.create_task(
            handle_pdf_processing(task_id, temp_pdf, temp_dir)
        )
        
        return JSONResponse({
            "task_id": task_id,
            "status": "processing"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_pdf_processing(task_id: str, pdf_path: str, output_dir: str):
    try:
        # 更新任务状态为处理中
        TASK_STATUS[task_id] = {"status": "processing"}
        
        # 异步处理PDF
        result = await process_pdf(pdf_path, output_dir)
        TASK_STATUS[task_id] = result
        
    except Exception as e:
        TASK_STATUS[task_id] = {
            "status": "failed",
            "error": str(e)
        }

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in TASK_STATUS:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = TASK_STATUS[task_id]
    return {
        "task_id": task_id,
        "status": result["status"],
        "result": result.get("output_files") if result["status"] == "completed" else result.get("error")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)