FROM python:12-alpine

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

CMD ["python", "./reboot-huawei.py"]
