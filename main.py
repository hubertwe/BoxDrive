import local

if __name__ == "__main__":
    observer = local.Observer('./test')
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()