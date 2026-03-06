#!/usr/bin/env python3
"""
Camera and phone presets for EXIF data generation.
Add new presets here to expand camera options.
"""

CAMERA_PRESETS = {
    # ========================================================================
    # DSLR & Mirrorless Cameras
    # ========================================================================
    "canon_r5": {
        "make":       "Canon",
        "model":      "Canon EOS R5",
        "lens_make":  "Canon",
        "software":   "Adobe Lightroom Classic 13.0",
        "lenses": [
            ("RF 50mm F1.2 L USM",       50,  (12, 10),  [(10,10),(12,10),(14,10),(18,10)]),
            ("RF 85mm F1.2 L USM",       85,  (12, 10),  [(12,10),(14,10),(18,10),(20,10)]),
            ("RF 24-70mm F2.8 L IS USM", 35,  (28, 10),  [(28,10),(35,10),(40,10),(56,10)]),
            ("RF 70-200mm F2.8 L IS USM",100, (28, 10),  [(28,10),(40,10),(56,10),(80,10)]),
        ],
        "iso_pool":  [100, 160, 200, 320, 400, 640, 800, 1600],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,125),(1,60)],
    },
    
    "nikon_z7": {
        "make":       "Nikon Corporation",
        "model":      "NIKON Z 7II",
        "lens_make":  "Nikon",
        "software":   "Capture NX-D 1.7.2 W",
        "lenses": [
            ("NIKKOR Z 50mm f/1.8 S",    50,  (18, 10),  [(18,10),(20,10),(28,10),(40,10)]),
            ("NIKKOR Z 85mm f/1.8 S",    85,  (18, 10),  [(18,10),(20,10),(28,10),(40,10)]),
            ("NIKKOR Z 24-70mm f/2.8 S", 35,  (28, 10),  [(28,10),(35,10),(40,10),(56,10)]),
        ],
        "iso_pool":  [64, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,125),(1,60)],
    },
    
    "sony_a7iv": {
        "make":       "SONY",
        "model":      "ILCE-7M4",
        "lens_make":  "Sony",
        "software":   "ILCE-7M4 v1.00",
        "lenses": [
            ("FE 50mm F1.2 GM",          50,  (12, 10),  [(12,10),(14,10),(18,10),(20,10)]),
            ("FE 85mm F1.4 GM",          85,  (14, 10),  [(14,10),(18,10),(20,10),(28,10)]),
            ("FE 24-70mm F2.8 GM II",    35,  (28, 10),  [(28,10),(35,10),(40,10),(50,10)]),
            ("FE 70-200mm F2.8 GM OSS II",135,(28, 10),  [(28,10),(40,10),(56,10),(80,10)]),
        ],
        "iso_pool":  [100, 200, 400, 800, 1600, 3200, 6400],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,125),(1,60)],
    },
    
    "fuji_xt5": {
        "make":       "FUJIFILM",
        "model":      "X-T5",
        "lens_make":  "FUJIFILM",
        "software":   "Digital Photo Professional 4.20.0",
        "lenses": [
            ("XF56mmF1.2 R WR",  56, (12, 10), [(12,10),(14,10),(18,10),(20,10)]),
            ("XF35mmF1.4 R",     35, (14, 10), [(14,10),(18,10),(20,10),(28,10)]),
            ("XF18-55mmF2.8-4 R LM OIS", 35, (28,10), [(28,10),(35,10),(40,10),(56,10)]),
        ],
        "iso_pool":  [125, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,125),(1,60)],
    },
    
    # ========================================================================
    # Mobile & Smartphones
    # ========================================================================
    "iphone_15": {
        "make":       "Apple",
        "model":      "iPhone 15 Pro",
        "lens_make":  "Apple",
        "software":   "17.2",
        "lenses": [
            ("iPhone 15 Pro back triple camera 6.765mm f/1.78", 7,  (178,100), [(178,100)]),
            ("iPhone 15 Pro back triple camera 2.22mm f/2.2",  2,  (220,100), [(220,100)]),
            ("iPhone 15 Pro back triple camera 12mm f/2.8",    12, (280,100), [(280,100)]),
        ],
        "iso_pool":  [32, 50, 64, 100, 200, 400, 800, 1600],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "iphone_15_max": {
        "make":       "Apple",
        "model":      "iPhone 15 Pro Max",
        "lens_make":  "Apple",
        "software":   "17.2",
        "lenses": [
            ("iPhone 15 Pro Max main camera 7.8mm f/1.78", 12,  (178,100), [(178,100)]),
            ("iPhone 15 Pro Max ultra wide 2.2mm f/2.2",  2,  (220,100), [(220,100)]),
            ("iPhone 15 Pro Max telephoto 12mm f/2.8",    12, (280,100), [(280,100)]),
        ],
        "iso_pool":  [32, 50, 64, 100, 200, 400, 800, 1600],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "samsung_s24": {
        "make":       "samsung",
        "model":      "SM-S921B",
        "lens_make":  "Samsung",
        "software":   "Samsung One UI 6.1",
        "lenses": [
            ("Samsung ISOCELL GN2 50MP f/1.8", 24, (180,100), [(180,100)]),
            ("Samsung ultra-wide 10MP f/2.2",  10, (220,100), [(220,100)]),
            ("Samsung telephoto 50MP f/3.0",   48, (300,100), [(300,100)]),
        ],
        "iso_pool":  [50, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "samsung_s24_ultra": {
        "make":       "samsung",
        "model":      "SM-S928B",
        "lens_make":  "Samsung",
        "software":   "Samsung One UI 6.1",
        "lenses": [
            ("Samsung ISOCELL HP2 200MP Ultra Wide f/1.7", 23, (170,100), [(170,100)]),
            ("Samsung ultra-wide 12MP f/2.2",  12, (220,100), [(220,100)]),
            ("Samsung telephoto 50MP f/3.4",   48, (340,100), [(340,100)]),
            ("Samsung periscope 10MP f/3.0",   100, (300,100), [(300,100)]),
        ],
        "iso_pool":  [40, 50, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "google_pixel_9": {
        "make":       "Google",
        "model":      "Pixel 9",
        "lens_make":  "Google",
        "software":   "Google Tensor Chip Image Processing",
        "lenses": [
            ("Pixel 9 main 50MP f/1.68", 22, (168,100), [(168,100)]),
            ("Pixel 9 super res zoom 2x", 42, (200,100), [(200,100)]),
            ("Pixel 9 ultra wide 10.5MP f/2.2", 11, (220,100), [(220,100)]),
        ],
        "iso_pool":  [50, 100, 200, 400, 800, 1600],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "google_pixel_9_pro": {
        "make":       "Google",
        "model":      "Pixel 9 Pro",
        "lens_make":  "Google",
        "software":   "Google Tensor Pro Image Processing",
        "lenses": [
            ("Pixel 9 Pro main 50MP f/1.68", 24, (168,100), [(168,100)]),
            ("Pixel 9 Pro super res zoom 5x", 42, (420,100), [(420,100)]),
            ("Pixel 9 Pro ultra wide 42MP f/2.2", 11, (220,100), [(220,100)]),
        ],
        "iso_pool":  [35, 50, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "oneplus_12": {
        "make":       "OnePlus",
        "model":      "CPH2577",
        "lens_make":  "OnePlus",
        "software":   "OxygenOS 14",
        "lenses": [
            ("OnePlus Hasselblad main 50MP f/1.6", 24, (160,100), [(160,100)]),
            ("OnePlus ultra-wide 48MP f/2.2", 14, (220,100), [(220,100)]),
            ("OnePlus telephoto 64MP f/2.6", 72, (260,100), [(260,100)]),
        ],
        "iso_pool":  [50, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "xiaomi_14": {
        "make":       "Xiaomi",
        "model":      "2404 (Xiaomi 14)",
        "lens_make":  "Leica",
        "software":   "HyperOS",
        "lenses": [
            ("Leica Summilux 50mm f/1.63", 50, (163,100), [(163,100)]),
            ("Leica Vario-Elmarit 30-70mm f/2.2-2.8", 42, (220,100), [(220,100)]),
            ("Leica Telefoto 75mm f/2.0", 75, (200,100), [(200,100)]),
        ],
        "iso_pool":  [50, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "xiaomi_14_ultra": {
        "make":       "Xiaomi",
        "model":      "2404 (Xiaomi 14 Ultra)",
        "lens_make":  "Leica",
        "software":   "HyperOS",
        "lenses": [
            ("Leica Summilux 23mm f/1.63 (Wide)", 23, (163,100), [(163,100)]),
            ("Leica Vario-Elmarit 32-70mm f/2.2-2.8", 50, (220,100), [(220,100)]),
            ("Leica Telefoto 75mm f/2.0", 75, (200,100), [(200,100)]),
            ("Leica Telefoto 120mm f/3.2", 120, (320,100), [(320,100)]),
        ],
        "iso_pool":  [40, 50, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "oppo_find_x7": {
        "make":       "OPPO",
        "model":      "CPH2547",
        "lens_make":  "Hasselblad by OPPO",
        "software":   "ColorOS 14",
        "lenses": [
            ("Hasselblad main camera 50MP f/1.6", 24, (160,100), [(160,100)]),
            ("Ultra wide 50MP f/2.0", 14, (200,100), [(200,100)]),
            ("Telephoto 50MP f/2.0 (3x zoom)", 72, (200,100), [(200,100)]),
        ],
        "iso_pool":  [50, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "honor_magic_6_pro": {
        "make":       "HONOR",
        "model":      "MOP-AL00",
        "lens_make":  "HONOR",
        "software":   "MagicOS 8.0",
        "lenses": [
            ("HONOR Magic6 Pro main 50MP f/1.4-4.0", 24, (140,100), [(140,100)]),
            ("HONOR ultra-wide 40MP f/2.2", 13, (220,100), [(220,100)]),
            ("HONOR periscope telephoto 50MP f/2.6", 70, (260,100), [(260,100)]),
        ],
        "iso_pool":  [32, 50, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
    
    "vivo_x100_ultra": {
        "make":       "vivo",
        "model":      "V2362A",
        "lens_make":  "Zeiss",
        "software":   "Funtouch OS 14",
        "lenses": [
            ("Zeiss APO 50mm f/1.6 Apo", 50, (160,100), [(160,100)]),
            ("Zeiss ultra-wide 50mm f/2.0", 13, (200,100), [(200,100)]),
            ("Zeiss Telefoto 85mm f/2.5", 90, (250,100), [(250,100)]),
        ],
        "iso_pool":  [50, 100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500),(1,250),(1,120),(1,60),(1,30)],
    },
}
