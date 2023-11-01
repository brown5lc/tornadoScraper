# tornadoScraper

`tornadoScraper` is a program designed to gather substantial amounts of Doppler radar velocity data, particularly during tornadic events. The primary purpose is to visualize this data, which will later be used for training a Convolutional Neural Network (CNN) in another project.

## Prerequisites

- Python 3.x

## Installation & Setup

1. **Clone the Repository**:
git clone https://github.com/YOUR_USERNAME/tornadoScraper.git

2. **Set Up a Virtual Environment** (Recommended):
Using a virtual environment is recommended to keep project dependencies isolated.

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate


3. **Install Dependencies**:

pip install -r requirements.txt

## Usage

python3 main.py [OPTIONS]

- Option 1: Nothing. The program will promt you if you want the data selection to be random or not, after which it will ask you how many images you want to generate. All the processed images can be found in the `radar_images` directory. 

- Option 2: `--debug` This is one of two debug modes. When this debug mode is used to run main, it must be followed by a number corresponding to a row in the `enriched_tornado_data.csv`. It will then proccess the data for that single event. This is useful for general debugging. 
- ...

## Debugging
`debug_mode` is disabled by default. To enable it call `visualize_radar_data` with the argument `True` in the 5th place. This can be seen on line `105` of the `main.py` file. 

If `debug_mode` is enabled in the program, you'll receive detailed logs and more information on the radar visualization:
- Radar Base Location
- Tornado Location
- X and Y Range for the visual data

## Contributing

If you'd like to contribute to the project, please follow the standard fork & pull request process. If you have any specific guidelines or steps you'd like contributors to follow, add them here.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
