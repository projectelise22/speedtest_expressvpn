## Utility for Testing Speed with ExpressVPN

### Notes
- Notes for creating the utility can be found here:

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
     --env=ACTIVATION_CODE=E27YSF3WBFBGUNAUTGMUBBO \ 
     --env=SERVER=smart \ 
     --env=PREFERRED_PROTOCOL=auto \ 
     --env=LIGHTWAY_CIPHER=auto \ 
     --cap-add=NET_ADMIN \ 
     --device=/dev/net/tun \ 
     --privileged \ 
     --tty=true \ 
     --name=name_of_container \ 
     image_name
   ```

3. **Run the Utility Script**:
   ```sh
   python speedtest_util.py
   ```
4. **You can change the locations in locations.json if needed**  

5. **Run the Tests for the Utility Script**:
   ```sh
   pytest tests/util_test.py -v
   
