#!/bin/bash


GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

clear
echo -e "${CYAN}=====================================================${NC}"
echo -e "${CYAN}           PYROUBOT AUTOMATIC SETUP HELPER           ${NC}"
echo -e "${CYAN}=====================================================${NC}"
echo -e "${YELLOW}Skrip ini akan membantu Anda membuat file .env${NC}"
echo -e "${YELLOW}Silakan masukkan data yang diminta.${NC}"
echo ""


ask_input() {
    local prompt="$1"
    local var_name="$2"
    local default_val="$3"
    
    if [ -n "$default_val" ]; then
        echo -e -n "${GREEN}$prompt ${YELLOW}[Default: $default_val]: ${NC}"
        read input
        if [ -z "$input" ]; then
            input="$default_val"
        fi
    else
        echo -e -n "${GREEN}$prompt: ${NC}"
        read input
    fi
    
    eval $var_name="'$input'"
}


echo -e "${CYAN}--- Konfigurasi Dasar (Telegram API) ---${NC}"
ask_input "Masukkan API ID (dari my.telegram.org)" "API_ID"
ask_input "Masukkan API HASH (dari my.telegram.org)" "API_HASH"
ask_input "Masukkan BOT TOKEN (dari @BotFather)" "BOT_TOKEN"
ask_input "Masukkan ID Telegram Pemilik (Owner ID)" "OWNER_ID"


echo ""
echo -e "${CYAN}--- Konfigurasi Database ---${NC}"
ask_input "Masukkan MONGO URL (mongodb+srv://...)" "MONGO_URL"


echo ""
echo -e "${CYAN}--- Konfigurasi Tambahan ---${NC}"
ask_input "Maksimal Userbot" "MAX_BOT" "100"
ask_input "Developer ID (Pisahkan dengan spasi jika banyak, default = Owner ID)" "DEVS" "$OWNER_ID"

echo ""
echo -e "${CYAN}--- API Tambahan (Boleh dikosongkan) ---${NC}"
ask_input "RemoveBG API Key (Biarkan kosong untuk default)" "RMBG_API"
ask_input "OpenAI API Key (Biarkan kosong jika tidak punya)" "OPENAI_API"

echo ""
echo -e "${CYAN}--- Konfigurasi Logging Group ---${NC}"
echo -e "${YELLOW}Info: Masukkan ID Grup untuk log (awalan -100...)${NC}"
ask_input "ID Grup Log Maker Ubot" "LOGS_MAKER_UBOT"
ask_input "ID Grup Blacklist (Opsional)" "BLACKLIST_CHAT"


echo ""
echo -e "${CYAN}Sedang membuat file .env...${NC}"

cat > .env <<EOL
# Bot Configuration
MAX_BOT=$MAX_BOT
DEVS=$DEVS
API_ID=$API_ID
API_HASH=$API_HASH
BOT_TOKEN=$BOT_TOKEN
OWNER_ID=$OWNER_ID

# Database
MONGO_URL=$MONGO_URL

# APIs
RMBG_API=$RMBG_API
OPENAI_API=$OPENAI_API

# Logging
BLACKLIST_CHAT=$BLACKLIST_CHAT
LOGS_MAKER_UBOT=$LOGS_MAKER_UBOT
EOL

echo -e "${GREEN}Sukses! File .env telah berhasil dibuat.${NC}"
echo ""

echo -e -n "${YELLOW}Apakah Anda ingin menginstall requirements.txt sekarang? (y/n): ${NC}"
read install_req

if [[ "$install_req" =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}Menginstall dependencies...${NC}"
    pip3 install -r requirements.txt
    echo -e "${GREEN}Instalasi selesai.${NC}"
else
    echo -e "${YELLOW}Melewati instalasi dependencies.${NC}"
fi

echo ""
echo -e "${CYAN}Setup selesai. Jalankan bot dengan perintah:${NC}"
echo -e "${GREEN}python3 -m PyroUbot${NC}"
