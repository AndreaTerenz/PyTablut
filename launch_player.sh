if (( $# >= 3 )) then
  python3.10 main.py "$1" -i "$2" -d "$3"
else 
  python3.10 main.py "$1" -i "$2"
fi