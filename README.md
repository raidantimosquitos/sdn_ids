# DOC API Zeek with mininet : 
## Set up 
### Import the project with git : 
```bash 
cd /home/p4
git clone https://github.com/clementperrotaimvp/api_zeek.git
cd api_zeek
```


2. Create Mininet architecture
```bash
sudo mn -c #cleanup 
miniedit
#then create manually the simple architechture
```


1. Start Zeek on the host zeek2 (We have to create a virtual interface because eth0 is already use)
```bash
sudo ip link add name zeek0 type dummy
sudo ip link set zeek0 up
sudo ip addr add 10.0.0.3/24 dev zeek0
sudo nano /usr/local/zeek/etc/node.cfg
#change to interface=zeek0
sudo /usr/local/zeek/bin/zeekctl cleanup
sudo /usr/local/zeek/bin/zeekctl deploy
sudo /usr/local/zeek/bin/zeekctl start
```

3. Install FASTAPI on Zeek Server
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

4. Launch the server
```bash
cd /home/p4/api_zeek
/home/p4/.local/bin/uvicorn main:app --reload
```


5. After experiment : Stop Zeek Server on zeek2 host

```bash
sudo /usr/local/zeek/bin/zeekctl stop
```
