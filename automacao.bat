@echo off
echo Iniciando a coleta de precos...
cd "C:\Projetos pessoais\ETL Monitoramento Baixos"

:: 1 Roda o robô
python scraper.py

:: 2 Sincroniza o banco de dados com o GitHub
echo Sincronizando com o GitHub...
git add historico_precos.db
git commit -m "Atualizacao automatica: Novos precos coletados"
git push
shutdown /s /t 20

echo Tudo pronto!