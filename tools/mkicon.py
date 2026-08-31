import zlib, struct, math, os

def png(path, w, h, px):
    raw = b''.join(b'\x00' + bytes(px[y*w*3:(y+1)*w*3]) for y in range(h))
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    out = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    open(path, 'wb').write(out)

def heart(x, y):            # implicit heart, x/y normalised, y up
    t = (x*x + y*y - 1)
    return t*t*t - x*x*y*y*y <= 0

def sparkle(x, y, cx, cy, r):   # four-point star
    dx, dy = abs(x-cx), abs(y-cy)
    if dx > r or dy > r: return False
    return (dx/r)**0.5 + (dy/r)**0.5 <= 1

def build(path, size, maskable=False):
    S = 3                                   # supersample factor
    heart_scale = 0.205 if maskable else 0.265
    radius = size if maskable else size*0.22 # rounded square vs full bleed
    px = bytearray(size*size*3)
    for y in range(size):
        for x in range(size):
            r = g = b = 0
            for sy in range(S):
                for sx in range(S):
                    fx, fy = x + (sx+0.5)/S, y + (sy+0.5)/S
                    u, v = fx/size, fy/size
                    # rounded-square mask
                    inside = True
                    if not maskable:
                        cx = min(max(fx, radius), size-radius)
                        cy = min(max(fy, radius), size-radius)
                        inside = (fx-cx)**2 + (fy-cy)**2 <= radius*radius
                    if not inside:
                        cr, cg, cb = 255, 255, 255
                    else:
                        # diagonal pink gradient: light bubblegum -> hot pink
                        t = (u*0.45 + v*0.75)
                        t = min(max(t, 0), 1)
                        cr = int(255 - 12*t); cg = int(122 - 90*t); cb = int(196 - 53*t)
                        hx = (u-0.5)/heart_scale
                        hy = (0.46-v)/heart_scale
                        if heart(hx, hy):
                            cr, cg, cb = 255, 255, 255
                        elif sparkle(u, v, 0.775, 0.245, 0.085) or sparkle(u, v, 0.24, 0.70, 0.055):
                            cr, cg, cb = 255, 214, 92
                    r += cr; g += cg; b += cb
            n = S*S
            i = (y*size + x)*3
            px[i] = r//n; px[i+1] = g//n; px[i+2] = b//n
    png(path, size, size, px)
    print('wrote', path, os.path.getsize(path), 'bytes')

os.makedirs('icons', exist_ok=True)
build('icons/icon-192.png', 192)
build('icons/icon-512.png', 512)
build('icons/icon-180.png', 180)
build('icons/icon-maskable-512.png', 512, maskable=True)
