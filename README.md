See the github wiki!

# This project uses a virtual environment.

To update the vitual environment requirements, run:

```bash
pip freeze > requirements.txt
```

To reproduce the virtual environment on a new system, run:
```bash
python -m venv venv
source venv/bin/activate
pip install git+https://github.com/westonforbes/my_little_snake_helpers.git
sudo apt update
sudo apt install cmake libjpeg62-turbo-dev -y
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd mjpg-streamer/mjpg-streamer-experimental
make
sudo make install
pip install -r requirements.txt
```
