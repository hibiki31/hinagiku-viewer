from verification.convert import debug
from verification.multithread_similer import main as sim_main
from verification.multithread_similer import app as sim_app
from verification.artist import main as artist_main

def main():
    # debug()
    # sim_main()
    # sim_app.run(debug=True)
    artist_main()


if __name__  == '__main__':
    main()