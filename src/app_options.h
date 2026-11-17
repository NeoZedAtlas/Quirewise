#ifndef QUIREWISE_APP_OPTIONS_H
#define QUIREWISE_APP_OPTIONS_H

#include <stddef.h>

typedef struct QwAppOptions {
    /* QW_RASTER_PAGE_MODE_A4 or QW_RASTER_PAGE_MODE_IMAGE. */
    int raster_page_mode;
    /* PDZ_PDF_PAGES_AUTO/BODY/BODY_ATT/ALL for PDG containers. */
    int pdz_page_rule;
    const char *archive_password;
    const char *pdf_password;
    size_t audio_track;
    const char *mdd_path;
    const char *pdf_font_path;
    int pdf_office_reflow;
    unsigned image_crop_left;
    unsigned image_crop_top;
    unsigned image_crop_right;
    unsigned image_crop_bottom;
    unsigned image_resize_width;
    unsigned image_resize_height;
    unsigned sheet_index;
} QwAppOptions;

#endif
