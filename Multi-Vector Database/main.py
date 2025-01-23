from unstructured.partition.pdf import partition_pdf
from extract_images import get_images_base64
from summarization import summarization,image_summarization
from vectorstore import vectorization


file_path = r"C:\Users\User\Desktop\VSCODE\Multi-Vector Database\DSKP - 41p.pdf"
images_output = r"C:\Users\User\Desktop\VSCODE\Multi-Vector Database\images"

try:
    chunks = partition_pdf(
        filename=file_path,
        infer_table_structure=True,            
        strategy="hi_res",                    
        extract_image_block_types=["Image","Table"],   # Add 'Table' to list to extract image of tables
        image_output_dir_path=images_output,   # if None, images and tables will saved in base64
        extract_image_block_to_payload=True,   # if true, will extract base64 for API usage
        chunking_strategy="by_title",          
        max_characters=10000,                  
        combine_text_under_n_chars=2000,       
        new_after_n_chars=6000,
    )
except Exception as e:
    print("An error occurred:", e)

tables = []
texts = []

for chunk in chunks:
    print("CHUNK: " , chunk)
    if "Table" in str(type(chunk)):
        tables.append(chunk)
        print("TABLES: " , tables)

    if "CompositeElement" in str(type((chunk))):
        texts.append(chunk)
        print("TEXTS: ", texts)

images = get_images_base64(chunks)

text_summaries,table_summaries = summarization(texts,tables)
image_summaries = image_summarization(images)


print("TEXTSSSSSSSSSSSSSS")
print(text_summaries)
print("TABLESSSSSSSSSSSSS")
print(table_summaries)
print("IMMMMAAAAAGGGEESSSSSSSSSSSSSS")
print(image_summaries)

retriever = vectorization(texts,tables,images,text_summaries,table_summaries,image_summaries)
docs = retriever.invoke(
    "What are the Performance Standards Guide for Listening Skills"
)

for doc in docs:
    print(str(doc) + "\n\n" + "-" * 80)
