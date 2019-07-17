from PIL import Image
import hashlib
import time
import os, sys
import math

##################################
# Распознавание цифр
##################################
class VectorCompare:
    def magnitude(self,concordance):
        total = 0
        for word,count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    def relation(self,concordance1, concordance2):
        relevance = 0
        topvalue = 0
        for word, count in concordance1.items():
            if word in concordance2:
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))


def buildvector(im):
    d1 = {}
    count = 0
    for i in im.getdata():
        d1[count] = i
        count += 1
    return d1
###################################

v = VectorCompare()

# Создание базы для сравнения
iconset = ['1','2','3','4','5','6','7','8','-','+']
imageset = []
for letter in iconset:
    for img in os.listdir('./iconset/%s/'%(letter)):
        temp = []
        if img != "Thumbs.db": # windows check...
            temp.append(buildvector(Image.open("./iconset/%s/%s"%(letter,img))))
        imageset.append({letter:temp})

# Счетчики точность/ошибка
correctcount = 0
wrongcount = 0

##################################
# Начало работы распознавания цифр
#
# Проверяем все капчи в папки example
for filename in os.listdir('./examples/'):
    try:
        im = Image.open("./examples/%s"%(filename)) #Открываем изображение.
    except:
        break

    print ("")
    print (filename)
    
    # - Поиск границ числового выражения
    width, height = im.size  #Определяем ширину и высоту (x,y) капчи    
    pix = im.load() #Выгружаем значения пикселей.    
    im2 = im          
    check = True #Если числовое выражение на границах изображения
    x0, xm, y0, ym = 0, 0, 0 ,0 #Границы числового выражения
    factor = 10
    for x in range(width):
        for y in range(height):
            a, b, c = pix[x, y]
            S = a + b + c            
            if (S > (((255 + factor) // 2) * 3)):
                im2.putpixel((x, y), (0, 0, 0))
                if (check):
                    check = False
                    y0, ym = y, y
                    x0, xm = x, x
                    #print ("Высота = ", x0, "Ширина = ", y0)
                if (xm < x):
                    xm = x
                    #print ("Высота макс = ", xm)
                elif (y0 > y):
                    y0 = y
                    #print ("Ширина начало = ", y0)
                elif (ym < y):
                    ym = y
                    #print ("Ширина макс = ", ym)
            else:
                im2.putpixel((x, y), (255, 255, 255))
                  
    border = (x0, y0-1, xm+1, ym+1)
    #image.crop(border).resize((35,25),Image.NEAREST).rotate(-25).save(nameImg[:len(nameImg)-4] + '_black.png', "PNG")
    #image.crop(border).rotate(0).save(nameImg[:len(nameImg)-4] + '_black.png', "PNG")
    #im2.crop(border).save(nameImg[:len(nameImg)-4] + '_black.gif', "GIF")


    # - Выравниваем числовое выражение, если оно повернуто
    print("CutNumbers")
    y0, ym = -1 ,-1
       
    degrees = 0
    check = False

    im3 = im2.crop(border)
    im2 = im3
    pix2 = im3.load() 
    #im2.rotate(-19, fillcolor = 255).save(nameImg[:len(nameImg)-4] + '_'+str(degrees) +'_rotate.gif', "GIF") 
    #Порачиваем пока белые пиксели не в одном ряду
    while not check:
        for y in range(im3.size[1]):
            for x in range(im3.size[0]):
                a, b, c = pix2[x, y]
                S = a + b + c 
                if (S == 0):                    
                    if  (x < im3.size[0] // 2):
                        #print("y0", x, y )
                        y0 = y
                        degrees += 1                        
                    else:
                        #print("ym", x, y )
                        ym = y
                        degrees -= 1
                        
                    #print("%s = %s // %s = %s // degrees = %s"%(y0, y, ym, y, degrees))        
                    if (y0 == y and ym == y):                    
                        #print ("Check True")
                        #image_rotate = image.rotate(degrees)
                        check = True
                        break
                        
            if ( not check):
                im3 = im2.rotate(degrees, fillcolor = (255, 255, 255))
                pix2 = im3.load()
                y0, ym = -1, -1
            else:
                
                break 
              
    
    #image.rotate(degrees).save(nameImg[:len(nameImg)-4] + '_'+str(degrees) +'_rotate.png', "PNG")
    #im3.save(nameImg[:len(nameImg)-4] + '_'+str(degrees) +'_rotate.gif', "GIF")    


    # - Вырезаем символы
    print("CutSymbols")
    x1, x2 = 0, 0        
    
    check = False
    
    width = im3.size[0]
    height = im3.size[1]    

    pix3 = im3.load()
    
    start_find = width // 4
    end_find = width - start_find*2
    #print(width, '=',height,'=', start_find,'=',end_find)

    count_wp = 2 #Минимальное число белых пикселей

    letters = [] # Список кординат символов    
    
    while 0 in (x1,x2):
        for x in range(end_find):
            mn = 0
            for y in range(height):                
                a, b, c = pix3[start_find + x, y]
                S = a + b + c 
                if (S == 0):
                        #print("white pix", start_find+i, j )
                        mn += 1

            if (mn < count_wp):
                #Находим первое совпадение для обрезания :) (потому что поиск с лево на право)
                if (x + start_find <= width // 2 and x1 == 0):                
                    x1 = x + start_find
                #Находи последнее совпадение для обрезания (так лучше обрезает)
                if (x + start_find > width // 2):                
                    x2 = x + start_find            
                

        if (x1 == 0 or x2 == 0):
            count_wp +=1

    letters.append((0, x1)) #Первый элемент в начале изображения
    letters.append((x1, x2))
    letters.append((x2, width))


    # - Сравнение символов и подсчет ошибок
    count = 0
    guessword = ""
    for letter in letters:
        m = hashlib.md5()
        im4 = im3.crop((letter[0], 0, letter[1], height)).convert("P").resize((15,25),Image.NEAREST)
        #m.update(("%s%s"%(time.time(),count)).encode('utf-8'))
        #im4.save(nameImg[:len(nameImg)-4] + "%s.gif"%(m.hexdigest()), "GIF")

        guess = []
        
        for image in imageset:
            for x,y in image.items():
                if len(y) != 0:
                    guess.append( ( v.relation(y[0],buildvector(im4)), x) )

        guess.sort(reverse=True)
        print ("",guess[0])
        guessword = "%s%s"%(guessword,guess[0][1])

        count += 1
        
    if guessword == filename[:-8]:
        correctcount += 1
    else:
        wrongcount += 1
#
###########################################

# Вывод точности        
print ("=======================")
correctcount = float(correctcount)
wrongcount = float(wrongcount)
print ("Correct Guesses - ",correctcount)
print ("Wrong Guesses - ",wrongcount)
print ("Percentage Correct - ", correctcount/(correctcount+wrongcount)*100.00)
print ("Percentage Wrong - ", wrongcount/(correctcount+wrongcount)*100.00)
    
