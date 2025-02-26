## Utility for Testing Speed with ExpressVPN

### Notes
- Notes for creating the utility can be found here: docs/
- I am currently checking how to publish this in Github Pages(html created from Notion). \
So to view the html files, please download them for now 😔.

### Usage

1. **Clone the Git Repository and Build the Docker Image**:
   ```sh
   git clone git@github.com:projectelise22/speedtest_expressvpn.git
   cd speedtest_expressvpn
   docker build -t image_name .
   ```

2. **Run the Container**:
   ```sh
   docker run --network=host -it \                      
     --env=ACTIVATION_CODE=your_activation_code \ 
     --env=SERVER=smart \ 
     --env=PREFERRED_PROTOCOL=auto \ 
     --env=LIGHTWAY_CIPHER=auto \ 
     --cap-add=NET_ADMIN \ 
     --device=/dev/net/tun \ 
     --privileged \ 
     --tty=true \ 
     --name=name_of_container \ 
     image_name \
     /bin/bash
   ```

3. **Run the Utility Script**:
   ```sh
   python speedtest_util.py
   ```
4. **You can change the locations in locations.json if needed**  

5. **Run the Tests for the Utility Script**:
   ```sh
   pytest tests/util_test.py -v

### Github References:
- Speedtest: https://github.com/robinmanuelthiel/speedtest.git
- ExpressVPN with Docker: https://github.com/polkaned/dockerfiles.git
   
