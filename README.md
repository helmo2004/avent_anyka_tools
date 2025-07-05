# Avent Anyka Tools
## Knowledge
### Boot Screen Images Raw
There is a partionen LOGO (LOGO.bin)
This contains a raw image with the given color-spec and resolution.
- SCD 89x/26: QVGA  320x240 (BGR888)
- SCD 92x/26: WQVGA 480×272 (BGR888)

how to create own image
```bash
# create own binary data for replacement in original image
convert input.jpg -resize 320x240\! -depth 8 -size 320x240 bgr:image.bin
```