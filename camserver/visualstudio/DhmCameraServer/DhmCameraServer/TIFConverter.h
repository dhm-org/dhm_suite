#include "FrameObserver.h"
#include <string.h>
#include "VimbaCPP/Include/VimbaCPP.h"
//#include "ProgramConfig.h"
#ifdef _WIN32
#include <Windows.h>
#endif //WIN32



namespace AVT {
namespace VmbAPI {
namespace Examples {

class TIFConverter 
{
public:
	TIFConverter(std:: string fname, FramePtr Data); 
	TIFConverter(std:: string fname); 
        TIFConverter(std::string fname, int frame_id, int imgSize, int width, int height);
	~TIFConverter();
	int convertToTIF();
	int convertToTIF(char* imageBuf);
	//getters and setters:
	int getShutter();
	int getGain();
	int getImageSize();
	int getWidth();
	int getHeight();
	int getFrameID();
	void setShutter(int Shutter);
	void setGain(int Gain);
	void setWidth(int Width);
	void setHeight(int Height);
	void setImageSize(int ImageSize);
private:
	
	void saveMetaDataToTxt();
	FramePtr imgData;
	// unsigned char* imgData;
	//std::string Filename;
	std::string Filename;
	//data types for meta data below:
	int shutter;
	int gain;
	int imagesize;
	int width;
	int height;
	int frameID;

};

}}} // namespace AVT::VmbAPI::Examples
