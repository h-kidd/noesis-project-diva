@ECHO OFF

set /p input="Input file: "
set /p output="Output folder: "
set output=%output:"=%
set /p count="Enter model count: "
set /p model="Enter model export file type: "
set /p tex="Enter texture export file type: "
set /a x=count-1

for /l %%i in (0, 1, %x%) do (
	Noesis.exe ?cmode %input% "%output%\model%%i.%model%" -modelindex %%i -texexsel -imgoutex .%tex%
)

pause
