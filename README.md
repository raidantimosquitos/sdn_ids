# DOC API 

1. Install FASTAPI on Zeek Server
On the main host 
```bash 
cd /home/p4 
pip download anyio-3.6.2-py3-none-any.whl
pip download click-8.1.3-py3-none-any.whl
pip download colorama-0.4.6-py2.py3-none-any.whl
pip download fastapi-0.92.0-py3-none-any.whl
pip download h11-0.14.0-py3-none-any.whl
pip download idna-3.4-py3-none-any.whl
pip download pydantic-1.10.5-cp310-cp310-win_amd64.whl
pip download sniffio-1.3.0-py3-none-any.whl
pip download starlette-0.25.0-py3-none-any.whl
pip download typing_extensions-4.5.0-py3-none-any.whl
pip download uvicorn-0.20.0-py3-none-any.whl
```
On the host zeek2 
```bash
cd /home/p4
pip install *.whl
```

2. Launch the server
```bash
cd /home/p4/api_zeek
/home/p4/.local/bin/uvicorn main:app --reload
```

