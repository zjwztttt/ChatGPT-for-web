app_id = ''
app_secret = ''

# Import the necessary libraries
import matplotlib.pyplot as plt
import qrcode

# Create the qr code instance
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Add data
data = "Your data here"
qr.add_data(data)
qr.make(fit=True)

# Create an image from the QR Code instance
img = qr.make_image()

# Show the image on the screen
plt.imshow(img)
plt.show()
