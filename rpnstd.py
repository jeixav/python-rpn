#TODO: should be able to search all rec tags and get the list of recs (handle or FstMeta)
#TODO: consistant naming in doc for; rec, data , meta, grid...
#TODO: class FstFields (a collection of related rec: levels,#...)
#TODO: expand FstGrid to accept multi-grids and work better with #-grids
#TODO: convert to/from NetCDF

"""Module Fstd contains the classes used to access RPN Standard Files (rev 2000)

    class FstFile    : a RPN standard file
    class FstRec     : a RPN standard file rec data (numpy.ndarray)) & meta (FstMeta)
    class FstGrid    : a RPN standard file grid Description, parameters (FstParm) and axis data/meta (FstRec)
    class FstMeta    : RPN standard file rec metadata
    class FstDate    : RPN STD Date representation; FstDate(DATESTAMP) or FstDate(YYYYMMDD,HHMMSShh)
    class FstDateRange: Range of FstData - DateStart,DateEnd,Delta

    class FstMapDesc :
    class FstExclude :
    class FstSelect  :
    class FstKeys    : search tags (nom, type, etiket, date, ip1, ip2, ip3)
    class FstDesc    : auxiliary tags (grtyp, ig1, ig2, ig3, ig4,  dateo, deet, npas, datyp, nbits)

    @author: Mario Lepine <mario.lepine@ec.gc.ca>
    @author: Stephane Chamberland <stephane.chamberland@ec.gc.ca>
    @date: 2009-09
"""
import types
import datetime
import pytz
import numpy
import Fstdc

__RPNSTD_VERSION__ = '1.2-dev'
__RPNSTD_LASTUPDATE__ = '2009-09'

# primary set of descriptors has two extra items, used to read/scan file
# handle carries the last handle associated with the keys ,
# or -1 if next match, or -2 if match is to start at beginning of file
X__PrimaryDesc={'nom':'    ','type':'  ','etiket':'            ',
                'date':-1,'ip1':-1,'ip2':-1,'ip3':-1,'handle':-2,'nxt':0,'fileref':None}

# descriptive part of the keys, returned by read/scan, needed for write
X__AuxiliaryDesc={'grtyp':'X','dateo':0,'deet':0,'npas':0,
               'ig1':0,'ig2':0,'ig3':0,'ig4':0,'datyp':0,'nbits':0}

# wild carded descriptive part of the keys (non initialized)
W__AuxiliaryDesc={'grtyp':' ','dateo':-1,'deet':-1,'npas':-1,
               'ig1':-1,'ig2':-1,'ig3':-1,'ig4':-1,'datyp':-1,'nbits':-1}

X__Criteres={'nom':['    '],'type':['  '],'etiket':['            '],
        'date':[-1],'ip1':[-1],'ip2':[-1],'ip3':[-1],
        'grtyp':[' '],'dateo':[-1],'deet':[-1],'npas':[-1],
        'ig1':[-1],'ig2':[-1],'ig3':[-1],'ig4':[-1],
        'ni':[-1],'nj':[-1],'nk':[-1],'datyp':[-1],'nbits':[-1]}

X__FullDesc={}
X__FullDesc.update(X__PrimaryDesc)
X__FullDesc.update(X__AuxiliaryDesc)

W__FullDesc={}
W__FullDesc.update(X__PrimaryDesc)
W__FullDesc.update(W__AuxiliaryDesc)

X__DateDebut=-1
X__DateFin=-1
X__Delta=0.0

def Predef_Grids():
  """Intentiate Predefined Grid configurations as global Objects

  global Grille_Amer_Nord, Grille_Europe, Grille_Inde, Grille_Hem_Sud, Grille_Canada, Grille_Maritimes
  global Grille_Quebec, Grille_Prairies, Grille_Colombie, Grille_USA, Grille_Global, Grille_GemLam10
  """
  global Grille_Amer_Nord, Grille_Europe, Grille_Inde, Grille_Hem_Sud, Grille_Canada, Grille_Maritimes
  global Grille_Quebec, Grille_Prairies, Grille_Colombie, Grille_USA, Grille_Global, Grille_GemLam10
  Grille_Amer_Nord=FstGrid(grtyp='N',ninj=(401,401),ig14=cxgaig('N',200.5,200.5,40000.0,21.0))  # PS 40km
  Grille_Europe=FstGrid(grtyp='N',ninj=(401,401),ig14=cxgaig('N',200.5,220.5,40000.0,-100.0))   # PS 40km
  Grille_Inde=FstGrid(grtyp='N',ninj=(401,401),ig14=cxgaig('N',200.5,300.5,40000.0,-170.0))     # PS 40km
  Grille_Hem_Sud=FstGrid(grtyp='S',ninj=(401,401),ig14=cxgaig('S',200.5,200.5,40000.0,21.0))    # PS 40km
  Grille_Canada=FstGrid(grtyp='N',ninj=(351,261),ig14=cxgaig('N',121.5,281.5,20000.0,21.0))     # PS 20km
  Grille_Maritimes=FstGrid(grtyp='N',ninj=(175,121),ig14=cxgaig('N',51.5,296.5,20000.0,-20.0))  # PS 20km
  Grille_Quebec=FstGrid(grtyp='N',ninj=(199,155),ig14=cxgaig('N',51.5,279.5,20000.0,0.0))       # PS 20km
  Grille_Prairies=FstGrid(grtyp='N',ninj=(175,121),ig14=cxgaig('N',86.5,245.5,20000.0,20.0))    # PS 20km
  Grille_Colombie=FstGrid(grtyp='N',ninj=(175,121),ig14=cxgaig('N',103.5,245.5,20000.0,30.0))   # PS 20km
  Grille_USA=FstGrid(grtyp='N',ninj=(351,261),ig14=cxgaig('N',121.0,387.5,20000.0,21.0))        # PS 20km
  Grille_Global=FstGrid(grtyp='L',ninj=(721,359),ig14=cxgaig('L',-89.5,180.0,0.5,0.5))          # LatLon 0.5 Deg
  Grille_GemLam10=FstGrid(grtyp='N',ninj=(1201,776),ig14=cxgaig('N',536.0,746.0,10000.0,21.0))  # PS 10km


def dump_keys_and_values(self):
    """Return a string with comma separated key=value of all parameters
    """
    result=''
    keynames = self.__dict__.keys()
    keynames.sort()
    for name in keynames:
        result=result+name+'='+repr(self.__dict__[name])+' , '
    return result[:-3]  # eliminate last blank comma blank sequence


LEVEL_KIND_MSL=0 #metres above sea level
LEVEL_KIND_SIG=1 #Sigma
LEVEL_KIND_PMB=2 #Pressure [mb]
LEVEL_KIND_ANY=3 #arbitrary code
LEVEL_KIND_MGL=4 #metres above ground level
LEVEL_KIND_HYB=5 #hybrid coordinates [hy]
LEVEL_KIND_TH=6 #theta [th]

def levels_to_ip1(levels,kind):
    """Encode level value into ip1 for the specified kind

    ip1_list = levels_to_ip1(level_list,kind)
    @param level_list list of level values [units depending on kind]
    @param kind   type of levels [units] to be encoded
        kind = 0: levels are in height [m] (metres) with respect to sea level
        kind = 1: levels are in sigma [sg] (0.0 -> 1.0)
        kind = 2: levels are in pressure [mb] (millibars)
        Looks like the following are not suppored yet in the fortran func convip
            kind = 3: levels are in arbitrary code
            kind = 4: levels are in height [M] (metres) with respect to ground level
            kind = 5: levels are in hybrid coordinates [hy]
            kind = 6: levels are in theta [th]
    @return list of encoded level values-tuple ((ip1new,ip1old),...)
    @exception TypeError if level_list is not a tuple or list
    @exception ValueError if kind is not an int in range of allowed kind

    Example of use (and doctest tests):

    >>> levels_to_ip1([0.,13.5,1500.,5525.,12750.],0)
    [(15728640, 12001), (8523608, 12004), (6441456, 12301), (6843956, 13106), (5370380, 14551)]
    >>> levels_to_ip1([0.,0.1,.02,0.00678,0.000003],1)
    [(32505856, 2000), (27362976, 3000), (28511552, 2200), (30038128, 2068), (32805856, 2000)]
    >>> levels_to_ip1([1024.,850.,650.,500.,10.,2.,0.3],2)
    [(39948288, 1024), (41744464, 850), (41544464, 650), (41394464, 500), (42043040, 10), (43191616, 1840), (44340192, 1660)]
    """
    if not type(levels) in (type(()),type([])):
        raise ValueError,'levels_to_ip1: levels should be a list or a tuple; '+levels.__repr__()
    if type(kind) <> type(0):
        raise TypeError,'levels_to_ip1: kind should be an int in range [0,6]; '+kind.__repr__()
    elif not kind in (0,1,2): #(0,1,2,3,4,5,6):
        raise ValueError,'levels_to_ip1: kind should be an int in range [0,6]; '+kind.__repr__()
    if type(levels) == type(()):
        ip1_list = Fstdc.level_to_ip1(list(levels),kind)
    else:
        ip1_list = Fstdc.level_to_ip1(levels,kind)
    if not ip1_list:
        raise TypeError,'levels_to_ip1: wrong args type; levels_to_ip1(levels,kind)'
    return(ip1_list)


def ip1_to_levels(ip1list):
    """Decode ip1 value into (level,kind)

    levels_list = ip1_to_levels(ip1list)
    @param ip1list list of ip1 values to decode
    @return list of decoded level values-tuple ((level,kind),...)
        kind = 0: levels are in height [m] (metres) with respect to sea level
        kind = 1: levels are in sigma [sg] (0.0 -> 1.0)
        kind = 2: levels are in pressure [mb] (millibars)
        kind = 3: levels are in arbitrary code
        kind = 4: levels are in height [M] (metres) with respect to ground level
        kind = 5: levels are in hybrid coordinates [hy]
        kind = 6: levels are in theta [th]
    @exception TypeError if ip1list is not a tuple or list

    Example of use (and doctest tests):

    >>> ip1_to_levels([0,1,1000,1199,1200,1201,9999,12000,12001,12002,13000])
    [(0.0, 2), (1.0, 2), (1000.0, 2), (1.0, 3), (0.0, 3), (4.9999998736893758e-05, 2), (0.79989999532699585, 1), (1.0, 1), (0.0, 0), (5.0, 0), (4995.0, 0)]
    >>> ip1_to_levels([15728640, 12001,8523608, 12004,6441456, 12301,6843956, 13106,5370380, 14551])
    [(0.0, 0), (0.0, 0), (13.5, 0), (15.0, 0), (1500.0, 0), (1500.0, 0), (5525.0, 0), (5525.0, 0), (12750.0, 0), (12750.0, 0)]
    >>> ip1_to_levels([32505856, 2000,27362976, 3000,28511552, 2200,30038128, 2068,32805856, 2000])
    [(0.0, 1), (0.0, 1), (0.10000000149011612, 1), (0.099999994039535522, 1), (0.019999999552965164, 1), (0.019999999552965164, 1), (0.0067799999378621578, 1), (0.0067999996244907379, 1), (3.0000001061125658e-06, 1), (0.0, 1)]
    >>> ip1_to_levels([39948288, 1024,41744464, 850,41544464, 650,41394464, 500,42043040, 10,43191616, 1840,44340192, 1660])
    [(1024.0, 2), (1024.0, 2), (850.0, 2), (850.0, 2), (650.0, 2), (650.0, 2), (500.0, 2), (500.0, 2), (10.0, 2), (10.0, 2), (2.0, 2), (2.0, 2), (0.30000001192092896, 2), (0.30000001192092896, 2)]
    """
    if not type(ip1list) in (type(()),type([])):
        raise TypeError,'ip1_to_levels: levels should be a list or a tuple'

    if type(ip1list) == type(()):
        levels = Fstdc.ip1_to_level(list(ip1list))
    else:
        levels = Fstdc.ip1_to_level(ip1list)
    if not levels:
        raise TypeError,'ip1_to_levels: wrong args type; ip1_to_levels(ip1list)'
    return(levels)


def cxgaig(grtyp,xg1,xg2=None,xg3=None,xg4=None):
    """Encode grid definition values into ig1-4 for the specified grid type

    (ig1,ig2,ig3,ig4) = cxgaig(grtyp,xg1,xg2,xg3,xg4):
    (ig1,ig2,ig3,ig4) = cxgaig(grtyp,(xg1,xg2,xg3,xg4)):

    @param grtyp
    @param xg1 xg1 value (float) or tuple of the form (xg1,xg2,xg3,xg4)
    @param xg2 xg2 value (float)
    @param xg3 xg3 value (float)
    @param xg4 xg4 value (float)
    @return Tuple of encoded grid desc values (ig1,ig2,ig3,ig4)
    @exception TypeError if args are of wrong type
    @exception ValueError if grtyp is not in ('A','B','E','G','L','N','S')

    Example of use (and doctest tests):

    >>> cxgaig('N',200.5, 200.5, 40000.0, 21.0)
    (2005, 2005, 2100, 400)
    >>> cxgaig('N',200.5, 220.5, 40000.0, 260.0)
    (400, 1000, 29830, 57333)
    >>> cxgaig('S',200.5, 200.5, 40000.0, 21.0)
    (2005, 2005, 2100, 400)
    >>> cxgaig('L',-89.5, 180.0, 0.5, 0.5)
    (50, 50, 50, 18000)
    >>> ig1234 = (-89.5, 180.0, 0.5, 0.5)
    >>> cxgaig('L',ig1234)
    (50, 50, 50, 18000)

    Example of bad use (and doctest tests):

    >>> cxgaig('L',-89.5, 180  , 0.5, 0.5)
    Traceback (most recent call last):
    ...
    TypeError: cxgaig error: ig1,ig2,ig3,ig4 should be of type real:(-89.5, 180, 0.5, 0.5)
    >>> cxgaig('I',-89.5, 180.0, 0.5, 0.5)
    Traceback (most recent call last):
    ...
    ValueError: cxgaig error: grtyp ['I'] must be one of ('A', 'B', 'E', 'G', 'L', 'N', 'S')
    """
    validgrtyp = ('A','B','E','G','L','N','S') #I
    if xg2 == xg3 == xg4 == None and type(xg1) in (type([]),type(())) and len(xg1) == 4:
        (xg1,xg2,xg3,xg4) = xg1
    if None in (grtyp,xg1,xg2,xg3,xg4):
        raise TypeError,'cxgaig error: missing argument, calling is cxgaig(grtyp,xg1,xg2,xg3,xg4)'
    elif not grtyp in validgrtyp:
        raise ValueError,'cxgaig error: grtyp ['+grtyp.__repr__()+'] must be one of '+validgrtyp.__repr__()
    elif not (type(xg1) == type(xg2) == type(xg3) == type(xg4) == type(0.)):
        raise TypeError,'cxgaig error: ig1,ig2,ig3,ig4 should be of type real:'+(xg1,xg2,xg3,xg4).__repr__()
    else:
       return(Fstdc.cxgaig(grtyp,xg1,xg2,xg3,xg4))


def cigaxg(grtyp,ig1,ig2=None,ig3=None,ig4=None):
    """Decode grid definition values into xg1-4 for the specified grid type

    (xg1,xg2,xg3,xg4) = cigaxg(grtyp,ig1,ig2,ig3,ig4):
    (xg1,xg2,xg3,xg4) = cigaxg(grtyp,(ig1,ig2,ig3,ig4)):

    @param grtyp
    @param ig1 ig1 value (int) or tuple of the form (ig1,ig2,ig3,ig4)
    @param ig2 ig2 value (int)
    @param ig3 ig3 value (int)
    @param ig4 ig4 value (int)
    @return Tuple of decoded grid desc values (xg1,xg2,xg3,xg4)
    @exception TypeError if args are of wrong type
    @exception ValueError if grtyp is not in ('A','B','E','G','L','N','S')

    Example of use (and doctest tests):

    >>> cigaxg('N',2005,  2005,  2100,   400)
    (200.5, 200.5, 40000.0, 21.0)
    >>> cigaxg('N',400,  1000, 29830, 57333)
    (200.50123596191406, 220.49647521972656, 40000.0, 260.0)
    >>> cigaxg('S',2005,  2005,  2100,   400)
    (200.5, 200.5, 40000.0, 21.0)
    >>> cigaxg('L',50,    50,    50, 18000)
    (-89.5, 180.0, 0.5, 0.5)
    >>> ig1234 = (50,    50,    50, 18000)
    >>> cigaxg('L',ig1234)
    (-89.5, 180.0, 0.5, 0.5)

    Example of bad use (and doctest tests):

    >>> cigaxg('L',50,    50,    50, 18000.)
    Traceback (most recent call last):
    ...
    TypeError: cigaxg error: ig1,ig2,ig3,ig4 should be of type int:(50, 50, 50, 18000.0)
    >>> cigaxg('I',50,    50,    50, 18000)
    Traceback (most recent call last):
    ...
    ValueError: cigaxg error: grtyp ['I'] must be one of ('A', 'B', 'E', 'G', 'L', 'N', 'S')
    """
    validgrtyp = ('A','B','E','G','L','N','S') #I
    if ig2 == ig3 == ig4 == None and type(ig1) in (type([]),type(())) and len(ig1) == 4:
        (ig1,ig2,ig3,ig4) = ig1
    if None in (grtyp,ig1,ig2,ig3,ig4):
        raise TypeError,'cigaxg error: missing argument, calling is cigaxg(grtyp,ig1,ig2,ig3,ig4)'
    elif not grtyp in validgrtyp:
        raise ValueError,'cigaxg error: grtyp ['+grtyp.__repr__()+'] must be one of '+validgrtyp.__repr__()
    elif not (type(ig1) == type(ig2) == type(ig3) == type(ig4) == type(0)):
        raise TypeError,'cigaxg error: ig1,ig2,ig3,ig4 should be of type int:'+(ig1,ig2,ig3,ig4).__repr__()
    else:
        return(Fstdc.cigaxg(grtyp,ig1,ig2,ig3,ig4))


class FstFile:
    """Python Class implementation of the RPN standard file interface
    instanciating this class actually opens the file
    deleting the instance close the file

    myFstFile = FstFile(name,mode)
    @param name file name (string)
    @param mode Type of file (string,optional), 'RND', 'SEQ', 'SEQ+R/O' or 'RND+R/O'

    @exception TypeError if name is not
    @exception IOError if unable to open file

    Examples of use:

    myFstFile = FstFile(name,mode)       #opens the file
    params = myFstFile.info(seachParams) #get matching record params
    params = myFstFile.info(FirstRecord) #get params of first rec on file
    params = myFstFile.info(NextMatch)   #get next matching record params
    myFstRec = myFstFile[seachParams]    #get matching record data and params
    myFstRec = myFstFile[FirstRecord]    #get data and params of first rec on file
    myFstRec = myFstFile[NextMatch]      #get next matching record data and params
    myFstFile[params]   = mydataarray    #append data and tags to file
    myFstFile[myFstRec] = myFstRec.d     #append data and tags to file
    myFstFile.write(myFstRec)            #append data and tags to file
    myFstFile.write(myFstRec,rewrite=True) #rewrite data and tags to file
    myFstFile.rewrite(myFstRec)            #rewrite data and tags to file
    myFstFile.append(myFstRec)             #append data and tags to file

    myFstFile[myFstRec] = None           #erase record
    myFstFile[params.handle] = None      #erase record
    del myFstFile                        #close the file

    >>> myFile = FstFile('testfile.fst')
    R.P.N. Standard File (2000)  testfile.fst  is open with options: RND+STD  UNIT= 999
    >>> del myFile
    file  999  is closed, filename= testfile.fst
    """
    def __init__(self,name=None,mode='RND+STD') :
        if (not name) or type(name) <> type(''):
            raise TypeError,'FstFile, need to provide a name for the file'
        self.filename=name
        self.lastread=None
        self.lastwrite=None
        self.options=mode
        self.iun = Fstdc.fstouv(0,self.filename,self.options)
        if (self.iun == None):
          raise IOError,(-1,'failed to open standard file',self.filename)
        else:
          print 'R.P.N. Standard File (2000) ',name,' is open with options:',mode,' UNIT=',self.iun

    def voir(self,options='NEWSTYLE'):
        """Print the file content listing"""
        Fstdc.fstvoi(self.iun,options)

    def __del__(self):
        """Close File"""
        if (self.iun != None):
          Fstdc.fstfrm(self.iun)
          print 'file ',self.iun,' is closed, filename=',self.filename
        del self.filename
        del self.lastread
        del self.lastwrite
        del self.options
        del self.iun

    def __getitem__(self,key):
        """Get the record, meta and data (FstRec), corresponding to the seach keys from file

        myrec = myfstfile[mykey]
        @param mykey search keys for FstFile.info()
        @return instance of FstRec with data and meta of the record; None if rec not found
        """
        params = self.info(key)         # 1 - get handle
        if params == None:              # oops !! not found
            return None
        target = params.handle
        array=Fstdc.fstluk(target)   # 2 - get data
        #TODO: make ni,nj,nk consistent?
        #TODO: update self.grid?
        return FstRec(array,params)

    def edit_dir_entry(self,key):
      """Edit (zap) directory entry referenced by handle

      myfstdfile.edit_dir_entry(myNewFstParams)

      myNewFstParams.handle must be a valid rec/file handle as retrieved by myfstdfile.info()
      """
      return(Fstdc.fst_edit_dir(key.handle,key.date,key.deet,key.npas,-1,-1,-1,key.ip1,key.ip2,key.ip3,
                                key.type,key.nom,key.etiket,key.grtyp,key.ig1,key.ig2,key.ig3,key.ig4,key.datyp))

    def info(self,key,list=False):
        """Seach file for next record corresponding to search keys
        Successive calls will go further in the file.
        Search index can be reset to begining of file with myfstfile.info(FirstRecord)
        If key.handle >=0, return key w/o search and w/o checking the file

        myfstparms = myfstfile.info(FirstRecord)
        myfstparms = myfstfile.info(mykeys)
        myfstparms = myfstfile.info(NextMatch)
        myfstparms = myfstfile.info(mykeys,list=True)
        @param mykeys search keys, can be an instance FstParm or derived classes (FstKeys, FstDesc, FstMeta, FstRec)
        @param list if true, return a list of all rec FstMeta matching the search keys (handle is then ignored)
        @return a FstMeta instance of the record with proper handle, return None if not found
        @exception TypeError if

        Accepted seach keys: nom,type,
                              etiket,ip1,ip2,ip3,datev,handle
        TODO: extend accepted seach keys to all FstMeta keys

        The myfstfile.lastread parameter is set with values of all latest found rec params
        """
        if isinstance(key,FstMeta):
            if list:
                mylist = Fstdc.fstinl(self.iun,key.nom,key.type,
                              key.etiket,key.ip1,key.ip2,key.ip3,
                              key.datev)
                mylist2 = []
                for item in mylist:
                    result=FstMeta()
                    result.update_by_dict(item)
                    result.fileref=self
                    mylist2.append(result)
                self.lastread=mylist[-1]
                return mylist2
            elif key.nxt == 1:               # get NEXT one thatmatches
                self.lastread=Fstdc.fstinf(self.iun,key.nom,key.type,
                              key.etiket,key.ip1,key.ip2,key.ip3,
                              key.datev,key.handle)
            else:                          # get FIRST one that matches
                if key.handle >= 0 :       # handle exists, return it
                    return key #TODO: may want to check if key.handle is valid
                self.lastread=Fstdc.fstinf(self.iun,key.nom,key.type,
                              key.etiket,key.ip1,key.ip2,key.ip3,
                              key.datev,-2)
        elif key==NextMatch:               # fstsui, return FstHandle instance
            self.lastread=Fstdc.fstinf(self.iun,' ',' ',' ',0,0,0,0,-1)
        else:
            raise TypeError,'FstFile.info(), search keys arg is not of a valid type'
        result=FstMeta()
        if self.lastread != None:
#            self.lastread.__dict__['fileref']=self
            result.update_by_dict(self.lastread)
            result.fileref=self
#            print 'DEBUG result=',result
        else:
            return None
        return result # return handle

    def __setitem__(self,index,value):
        """[re]write data and tags of rec in RPN STD file

        myfstfile.info[myfstparms] = mydataarray
        myfstfile.info[myfstrec]   = myfstrec.d
        myfstfile.info[myfstrec]   = None #erase the record corresponding to myfstrec.handle
        myfstfile.info[myfstrec.handle] = None #erase the record corresponding to handle

        @param myfstparms  values of rec parameters, must be a FstMeta instance (or derived class)
        @param mydataarray data to be written, must be numpy.ndarray instance
        @exception TypeError if args are of wrong type
        @exception TypeError if params.handle is not valid when erasing (value=None)
        """
        if value == None:
            if (isinstance(index,FstParm)): # set of keys
                target = index.handle
            elif type(index) == type(0):  # handle
                target = index
            else:
                raise TypeError, 'FstFile: index must provide a valid handle to erase a record'
            print 'erasing record with handle=',target,' from file'
            self.lastwrite=Fstdc.fsteff(target)
        elif isinstance(index,FstMeta) and type(value) == numpy.ndarray:
            self.lastwrite=0
#            print 'writing data',value.shape,' to file, keys=',index
#            print 'dict = ',index.__dict__
            if (value.flags.farray):
              print 'fstecr Fortran style array'
              Fstdc.fstecr(value,
                         self.iun,index.nom,index.type,index.etiket,index.ip1,index.ip2,
                         index.ip3,index.dateo,index.grtyp,index.ig1,index.ig2,index.ig3,
                         index.ig4,index.deet,index.npas,index.nbits)
            else:
              print 'fstecr C style array'
              Fstdc.fstecr(numpy.reshape(numpy.transpose(value),value.shape),
                         self.iun,index.nom,index.type,index.etiket,index.ip1,index.ip2,
                         index.ip3,index.dateo,index.grtyp,index.ig1,index.ig2,index.ig3,
                         index.ig4,index.deet,index.npas,index.nbits)
        else:
           raise TypeError,'FstFile write: value must be an array and index must be FstMeta or FstRec'

    def write(self,data,meta=None,rewrite=False):
        """Write a FstRec to the file

        myFstRec.write(myFstRec)
        myFstRec.write(myArray,myFstMeta)
        myFstRec.write(myFstRec,rewrite=false)
        myFstRec.write(myArray,myFstMeta,rewrite=true)

        @param myFstRec an instance of FstRec with data and meta/params to be written
        @param myArray an instance of numpy.ndarray
        @param myFstMeta an instance of FstMeta with meta/params to be written
        @exception TypeError if args are of wrong type
        """
        if meta == None and isinstance(data,FstRec):
            if rewrite and data.handle >=0:
                Fstdc.fsteff(data.handle)
            self.__setitem__(data,data.d)
        elif isinstance(meta,FstMeta) and type(data) == numpy.ndarray:
            if rewrite and meta.handle >=0:
                Fstdc.fsteff(meta.handle)
            self.__setitem__(meta,data)
        else:
            raise TypeError,'FstFile write: value must be an array and index must be FstMeta or FstRec'

    def append(self,data,meta=None):
        """Append a FstRec to the file, shortcut for write(...,rewrite=False)

        myFstRec.append(myFstRec)
        myFstRec.append(myArray,myFstMeta)

        @param myFstRec an instance of FstRec with data and meta/params to be written
        @param myArray an instance of numpy.ndarray
        @param myFstMeta an instance of FstMeta with meta/params to be written
        @exception TypeError if args are of wrong type
        """
        self.write(data,meta,rewrite=False)

    def rewrite(self,data,meta=None):
        """Write a FstRec to the file, rewrite if record handle is found and exists
        shortcut for write(...,rewrite=True)

        myFstRec.rewrite(myFstRec)
        myFstRec.rewrite(myArray,myFstMeta)

        @param myFstRec an instance of FstRec with data and meta/params to be written
        @param myArray an instance of numpy.ndarray
        @param myFstMeta an instance of FstMeta with meta/params to be written
        @exception TypeError if args are of wrong type
        """
        self.write(data,meta,rewrite=True)


class FstParm:
    """Base methods for all RPN standard file descriptor classes
    """
    def __init__(self,model,reference,extra):
        for name in reference.keys():            # copy initial values from reference
            self.__dict__[name]=reference[name]  # bypass setatttr method for new attributes
        if model != None:
            if isinstance(model,FstParm):        # update with model attributes
               self.update(model)
            else:
                raise TypeError,'FstParm.__init__: model must be an FstParm class instances'
        for name in extra.keys():                # add extras using own setattr method
            setattr(self,name,extra[name])

    def allowedKeysVals(self):
        """function must be defined in subclass, return dict of allowed keys/vals"""
        return {}

    def update(self,with):
        """Replace Fst attributes of an instance with Fst attributes from another
        values not in list of allowed parm keys are ignored
        also update to wildcard (-1 or '') values

        myfstparm.update(otherfstparm) #update myfstparm values with otherfstparm
        @param otherfstparm list of params=value to be updated, instance of FstParm or derived class
        @exception TypeError if otherfstparm is of wrong class
        """
        allowedKeysVals = self.allowedKeysVals()
        if isinstance(with,FstParm):  # check if class=FstParm
            for name in with.__dict__.keys():
                if (name in self.__dict__.keys()) and (name in allowedKeysVals.keys()):
                    self.__dict__[name]=with.__dict__[name]
                #else:
                #    print "cannot set:"+name+repr(allowedKeysVals.keys())
        else:
            raise TypeError,'FstParm.update: can only operate on FstParm class instances'

    def update_cond(self,with):
        """Conditional Replace Fst attributes if not wildcard values
        values not in list of allowed parm keys are ignored
        value that are wildcard (-1 or '') are ignored

        myfstparm.update_cond(otherfstparm) #update myfstparm values with otherfstparm
        @param otherfstparm list of params=value to be updated, instance of FstParm or derived class
        @exception TypeError if otherfstparm is of wrong class
        """
        allowedKeysVals = self.allowedKeysVals()
        if isinstance(with,FstParm):  # check if class=FstParm
            for name in with.__dict__.keys():
                if (name in self.__dict__.keys()) and (name in allowedKeysVals.keys()):
                    if (with.__dict__[name] != W__FullDesc[name]):
                        self.__dict__[name]=with.__dict__[name]
        else:
            raise TypeError,'FstParm.update_cond: can only operate on FstParm class instances'

    def update_by_dict(self,with):
        """Replace Fst attributes of an instance with dict of {key:value,}
        keys not in list of allowed parm keys are ignored
        also update to wildcard (-1 or '') values

        myfstparm.update_by_dict(paramsdict) #update myfstparm values with paramsdict
        @param paramsdict dict of {key:value,}
        @exception TypeError if paramsdict is of wrong type
        """
        if type(with) == type({}):
            for name in with.keys():
                if name in self.__dict__.keys():
                    setattr(self,name,with[name])
        else:
            raise TypeError,'FstParm.update_by_dict: arg should by a dict'

    def update_by_dict_from(self,frm,with):
        for name in with.keys():
            if name in self.__dict__.keys():
                setattr(self,name,frm.__dict__[name])

    def __setattr__(self,name,value):   # this method cannot create new attributes
        """Set FstParm attribute value, will only accept a set of allowed attribute (rpnstd params list)
        myfstparm.ip1 = 0
        @exception TypeError if value is of the wrong type for said attribute
        @exception ValueError if not a valid/allowed attribute
        """
        if name in self.__dict__.keys():                   # is attribute name valid ?
            if type(value) == type(self.__dict__[name]):   # right type (string or int))
                if type(value) == type(''):
                    reflen=len(self.__dict__[name])        # string, remember length
                    self.__dict__[name]=(value+reflen*' ')[:reflen]
                else:
                    self.__dict__[name]=value              # integer
            else:
                if self.__dict__[name] == None:
                   self.__dict__[name]=value
                else:
                    raise TypeError,'FstParm: Wrong type for attribute '+name+'='+value.__repr__()
        else:
            raise ValueError,'FstParm: attribute'+name+'does not exist for class'+self.__class__.__repr__()

    def __setitem__(self,name,value):
        self.__setattr__(name,value)

    def __getitem__(self,name):
        return self.__dict__[name]

    def findnext(self,flag=True):
        """set/reset next match flag
        myfstparm.findnext(True)  #set findnext flag to true
        myfstparm.findnext(False) #set findnext flag to false
        """
        self.nxt = 0
        if flag:
            self.nxt = 1
        return self

    def wildcard(self):
        """Reset keys to undefined/wildcard"""
        self.update_by_dict(W__FullDesc)

    def __str__(self):
        return dump_keys_and_values(self)

    def __repr__(self):
        return self.__dict__.__repr__()


class FstKeys(FstParm):
    """RPN standard file Primary descriptors class, used to search for a record.
    Descriptors are:
    {'nom':'    ','type':'  ','etiket':'            ','date':-1,'ip1':-1,'ip2':-1,'ip3':-1,'handle':-2,'nxt':0,'fileref':None}
    TODO: give examples of instanciation
    """
    def __init__(self,model=None,**args):
        FstParm.__init__(self,model,self.allowedKeysVals(),args)

    def allowedKeysVals(self):
        """Return a dict of allowed Keys/Vals"""
        return {'nom':'    ','type':'  ','etiket':'            ','datev':-1,'ip1':-1,'ip2':-1,'ip3':-1,'handle':-2,'nxt':0,'fileref':None}

class FstDesc(FstParm):
    """RPN standard file Auxiliary descriptors class, used when writing a record or getting descriptors from a record.
    Descriptors are:
    {'grtyp':'X','dateo':0,'deet':0,'npas':0,'ig1':0,'ig2':0,'ig3':0,'ig4':0,'datyp':0,'nbits':0,'xaxis':None,'yaxis':None,'xyref':(None,None,None,None,None),'griddim':(None,None)}
    TODO: give examples of instanciation
    """
    def __init__(self,model=None,**args):
        FstParm.__init__(self,model,self.allowedKeysVals(),args)

    def allowedKeysVals(self):
        """Return a dict of allowed Keys/Vals"""
        return {'grtyp':'X','dateo':0,'deet':0,'npas':0,'ig1':0,'ig2':0,'ig3':0,'ig4':0,'datyp':0,'nbits':0,'ni':-1,'nj':-1,'nk':-1}

class FstMeta(FstKeys,FstDesc):
    """RPN standard file Full set (Primary + Auxiliary) of descriptors class, needed to write a record, can be used for search.

    Descriptors are:
        'nom':'    ',
        'type':'  ',
        'etiket':'            ',
        'ip1':-1,'ip2':-1,'ip3':-1,
        'ni':-1,'nj':-1,'nk':-1,
        'dateo':0,
        'deet':0,
        'npas':0,
        'grtyp':'X',
        'ig1':0,'ig2':0,'ig3':0,'ig4':0,
        'datyp':0,
        'nbits':0,
        'handle':-2,
        'nxt':0,
        'fileref':None,
        'datev':-1

    Examples of use (also doctests):

    >>> myFstMeta = FstMeta() #New FstMeta with default/wildcard descriptors
    >>> d = myFstMeta.__dict__.items()
    >>> d.sort()
    >>> d
    [('dateo', 0), ('datev', -1), ('datyp', 0), ('deet', 0), ('etiket', '            '), ('fileref', None), ('grtyp', 'X'), ('handle', -2), ('ig1', 0), ('ig2', 0), ('ig3', 0), ('ig4', 0), ('ip1', -1), ('ip2', -1), ('ip3', -1), ('nbits', 0), ('ni', -1), ('nj', -1), ('nk', -1), ('nom', '    '), ('npas', 0), ('nxt', 0), ('type', '  ')]
    >>> myFstMeta = FstMeta(nom='GZ',ip2=1)  #New FstMeta with all descriptors to wildcard but nom,ip2
    >>> d = myFstMeta.__dict__.items()
    >>> d.sort()
    >>> d
    [('dateo', 0), ('datev', -1), ('datyp', 0), ('deet', 0), ('etiket', '            '), ('fileref', None), ('grtyp', 'X'), ('handle', -2), ('ig1', 0), ('ig2', 0), ('ig3', 0), ('ig4', 0), ('ip1', -1), ('ip2', 1), ('ip3', -1), ('nbits', 0), ('ni', -1), ('nj', -1), ('nk', -1), ('nom', 'GZ  '), ('npas', 0), ('nxt', 0), ('type', '  ')]
    >>> myFstMeta.ip1
    -1
    >>> myFstMeta2 = myFstMeta #shallow copy (reference)
    >>> myFstMeta2.ip1 = 9 #this will also update myFstMeta.ip1
    >>> myFstMeta.ip1
    9
    >>> myFstMeta2 = FstMeta(myFstMeta)   #make a deep-copy
    >>> myFstMeta.ip3
    -1
    >>> myFstMeta2.ip3 = 9 #this will not update myFstMeta.ip3
    >>> myFstMeta.ip3
    -1
    >>> myFstMeta2 = FstMeta(myFstMeta,nom='GZ',ip2=8)   #make a deep-copy and update nom,ip2 values
    >>> myFstMeta.ip2
    1
    >>> myFstMeta2.ip2
    8
    """
    def __init__(self,model=None,**args):
        FstParm.__init__(self,model,self.allowedKeysVals(),args)
        if model != None:
            if isinstance(model,FstParm):
                self.update(model)
            else:
                raise TypeError,'FstMeta: cannot initialize from arg #1'
        for name in args.keys(): # and update with specified attributes
            setattr(self,name,args[name])

    def allowedKeysVals(self):
        """Return a dict of allowed Keys/Vals"""
        a = FstKeys.allowedKeysVals(self)
        a.update(FstDesc.allowedKeysVals(self))
        return a

    def getaxis(self,axis=None):
        """Return the grid axis rec of grtyp ('Z','Y','#')

        (myFstRecX,myFstRecY) = myFstMeta.getaxis()
        myFstRecX = myFstMeta.getaxis('X')
        myFstRecY = myFstMeta.getaxis('Y')
        """
        if not (self.grtyp in ('Z','Y','#')):
            raise ValueError,'getaxis error: can not get axis from grtyp=',self.grtyp
        if (self.xaxis == None and self.yaxis == None):
            searchkeys = FstKeys(ip1=self.ig1,ip2=self.ig2)
            if self.grtyp != '#':
                searchkeys.update_by_dict({'ip3':self.ig3})
            searchkeys.nom = '>>'
            xaxisrec = self.fileref[searchkeys]
            searchkeys.nom = '^^'
            yaxisrec = self.fileref[searchkeys]
            if (xaxiskeys == None or yaxiskeys == None):
                raise ValueError,'getaxis error: axis grid descriptors (>>,^^) not found'
            self.xaxis = xaxisrec
            self.yaxis = yaxisrec
            self.xyref = (xaxisrec.grtyp,xaxisrec.ig1,xaxisrec.ig2,xaxisrec.ig3,xaxisrec.ig4)
            ni=xaxisrec.d.shape[0]
            nj=yaxisrec.d.shape[1]
            self.griddim=(ni,nj)
        axisrec = FstMeta()
        axisrec.xyref = self.xyref
        axisrec.griddim = self.griddim
        if axis == 'X':
            return xaxisrec
        elif axis == 'Y':
            return yaxisrec
            #axisdata=self.yaxis.ravel()
        return (xaxisrec,yaxisrec)


class FstCriterias:
    "Base methods for RPN standard file selection criteria input filter classes"
    def __init__(self,reference,exclu,extra):
        self.__dict__['exclu'] = exclu
        for name in reference.keys():            # copy initial values from reference
            self.__dict__[name]=[]+reference[name]  # bypass setatttr method for new attributes
        for name in extra.keys():                # add extras using own setattr method
            setattr(self,name,extra[name])

    def update(self,with):
        "Replace Fst attributes of an instance with Fst attributes from another"
        if isinstance(with,FstCriterias) and isinstance(self,FstCriterias):  # check if class=FstParm
            for name in with.__dict__.keys():
                if (name in self.__dict__.keys()) and (name in X__Criteres.keys()):
                    self.__dict__[name]=with.__dict__[name]
        else:
            raise TypeError,'FstParm.update: can only operate on FstCriterias class instances'

    def update_cond(self,with):
        "Conditional Replace Fst attributes if not wildcard values"
        if isinstance(with,FstCriterias) and isinstance(self,FstCriterias):  # check if class=FstCriterias
            for name in with.__dict__.keys():
                if (name in self.__dict__.keys()) and (name in X__Criteres.keys()):
                    if (with.__dict__[name] != X__Criteres[name]):
                        self.__dict__[name]=with.__dict__[name]
        else:
            raise TypeError,'FstCriterias.update_cond: can only operate on FstCriterias class instances'

    def update_by_dict(self,with):
        for name in with.keys():
            if name in self.__dict__.keys():
                setattr(self,name,with[name])

    def isamatch(self,with):
        "Check attributes for a match, do not consider wildcard values"
        global X__DateDebut,X__DateFin,X__Delta
        if isinstance(with,FstParm) and isinstance(self,FstCriterias):  # check if class=FstParm
            match = 1
            for name in with.__dict__.keys():
                if (name in self.__dict__.keys()) and (name in X__FullDesc.keys()):
                    if (self.__dict__[name] != X__Criteres[name]):      # check if wildcard
                        if (name == 'date'):
                            print 'Debug isamatch name=',name
                            if (X__DateDebut != -1) or (X__DateFin != -1):      # range of dates
                                print 'Debug range de date debut fin delta',X__DateDebut,X__DateFin,X__Delta
                                print 'Debug range with self',name,with.__dict__[name],self.__dict__[name]
                                match = match & Fstdc.datematch(with.__dict__[name],X__DateDebut,X__DateFin,X__Delta)
                            else:
                                print 'Debug check ',name,with.__dict__[name],self.__dict__[name]
                                match = match & (with.__dict__[name] in self.__dict__[name])
                        else:
                            print 'Debug check ',name,with.__dict__[name],self.__dict__[name]
                            match = match & (with.__dict__[name] in self.__dict__[name])
            return match
        else:
            raise TypeError,'FstCriterias.isamatch: can only operate on FstParm, FstCriterias class instances'

    def __setattr__(self,name,values):   # this method cannot create new attributes
        if name in self.__dict__.keys():                   # is attribute name valid ?
            if type(values) == type([]):
                self.__dict__[name]=[]
                for value in values:
                    if type(value) == type(''):
                        reflen=len(X__Criteres[name][0])        # string, remember length
                        self.__dict__[name].append((value+reflen*' ')[:reflen])
                    else:
                        self.__dict__[name].append(value)              # integer
            else:
                self.__dict__[name]=[]
                if type(values) == type(''):
                    reflen=len(X__Criteres[name][0])        # string, remember length
                    self.__dict__[name].append((values+reflen*' ')[:reflen])
                else:
                    self.__dict__[name].append(values)              # integer
        else:
            raise ValueError,'attribute'+name+'does not exist for class '+self.__class__.__repr__()

    def __str__(self):
        return dump_keys_and_values(self)

class FstSelect(FstCriterias):
    "Selection criterias for RPN standard file input filter"
    def __init__(self,**args):
        FstCriterias.__init__(self,X__Criteres,0,args)

class FstExclude(FstCriterias):
    "Exclusion criterias for RPN standard file input filter"
    def __init__(self,**args):
        FstCriterias.__init__(self,X__Criteres,1,args)


class FstGrid(FstParm):
    """RPNSTD-type grid description

    myFstGrid = FstGrid(grtyp='Z',xyaxis=(myFstRecX,myFstRecY))
    myFstGrid = FstGrid(grtyp='#',ninj=(200,150),ij0=(1,1),xyaxis=(myFstRecX,myFstRecY))
    myFstGrid = FstGrid(myFstRec)
    myFstGrid = FstGrid(keys=myFstRec)
    myFstGrid = FstGrid(myFstRec,xyaxis=(myFstRecX,myFstRecY))

    @param keys
    @param xyaxis
    @param ninj
    @param grtyp
    @param ij0
    @param ig14
    @exception ValueError
    @exception TypeError

    >>> g = FstGrid(grtyp='N',ig14=(1,2,3,4),ninj=(200,150))
    >>> g
    {'shape': (200, 150), 'grtyp': 'N', 'xyaxis': (None, None), 'ig14': (1, 2, 3, 4)}
    >>> g2 = FstGrid(g)
    >>> g2
    {'shape': (200, 150), 'grtyp': 'N', 'xyaxis': (None, None), 'ig14': (1, 2, 3, 4)}
    >>> d = FstMeta(grtyp='N',ig1=1,ig2=2,ig3=3,ig4=4,ni=200,nj=150)
    >>> g3 = FstGrid(d)
    >>> g3
    {'shape': (200, 150), 'grtyp': 'N', 'xyaxis': (None, None), 'ig14': (1, 2, 3, 4)}

    Icosahedral Grid prototype:
    grtyp = I
    ig1 = griddiv
    ig2 = grid tile (1-10) 2d, 0=NP,SP,allpoints (1D vect)
    ig3,ig4

    #(I) would work much the same way as #(L) ?
    """
    xyaxis = (None,None)

    def allowedKeysVals(self):
        return {
            'grtyp':'X',
            'ig14':(0,0,0,0),
            'shape':(0,0),
            'xyaxis':(None,None)
        }

    def getValidgrtyp(self):
        return ('A','B','E','G','L','N','S','Z','Y','#') #'X'

    def __init__(self,keys=None,xyaxis=(None,None),ninj=(None,None),grtyp=None,ij0=None,ig14=(None,None,None,None)):
        FstParm.__init__(self,None,self.allowedKeysVals(),{})
        #mode 1: grtype,ig14,ninj        ['A','B','E','G','L','N','S']
        #mode 2: grtype,xyaxis           [Z,Y]
        #mode 3: grtype,ninj,ij0,xyaxis  [#]
        #mode 4: keys
        #mode 5: keys,xyaxis
        if grtyp != None:
            if keys != None:
                raise ValueError,'FstGrid: cannot specify both grtyp and keys'
            if grtyp in self.getValidgrtyp():
                self.grtyp = grtyp
                if grtyp in ('Z','Y','#'):
                    if not (type(xyaxis) in (type([]),type(())) and len(xyaxis)==2
                        and isinstance(xyaxis[0],FstRec)
                        and isinstance(xyaxis[1],FstRec)):
                        raise TypeError,'FstGrid: xyaxis must be (FstRec,FstRec)'
                    self.shape = (xyaxis[0].d.shape[0],xyaxis[1].d.shape[1])
                    self.ig14= (xyaxis[0].ip1,xyaxis[0].ip2,xyaxis[0].ip3,0)
                    self.xyaxis = xyaxis
                    if grtyp == '#':
                        if not( type(ninj) in (type([]),type(())) and len(ninj)==2
                            and (type(ninj[0]) == type(ninj[1]) == type(0))
                            and type(ij0) in (type([]),type(())) and len(ij0)==2
                            and (type(ij0[0]) == type(ij0[1]) == type(0))):
                            raise TypeError,'FstGrid: ninj and ij0 must be (int,int)'
                        #TODO: check that these are inbound of xyaxis dims
                        self.shape = ninj
                        self.ig14= (xyaxis[0].ip1,xyaxis[0].ip2,ij0[0],ij0[1])
                else:
                    if type(ig14) in (type([]),type(())) and len(ig14)==4 \
                        and (type(ig14[0]) == type(ig14[1]) == type(ig14[2]) == type(ig14[3]) == type(0)) \
                        and type(ninj) in (type([]),type(())) and len(ninj)==2 \
                        and (type(ninj[0]) == type(ninj[1]) == type(0)):
                        self.ig14 = ig14
                        self.shape = ninj
                    else:
                        raise TypeError,'FstGrid: ig14 must be (int,int,int,int) and ninj must be (int,int)'
            else:
                raise ValueError,'FstGrid: gridtype must be one of '+repr(self.getValidgrtyp())
        elif isinstance(keys,FstMeta):
            if keys.grtyp in ('Z','Y','#'):
                xyaxis = keys.getaxis()
                if keys.grtyp == '#':
                    self.__init__(grtyp=keys.grtyp,ninj=(keys.ni,keys.nj),ij0=(keys.ig3,keys.ig4),xyaxis=xyaxis)
                else:
                    self.__init__(grtyp=keys.grtyp,xyaxis=xyaxis)
            else:
                self.__init__(grtyp=keys.grtyp,ninj=(keys.ni,keys.nj),ig14=(keys.ig1,keys.ig2,keys.ig3,keys.ig4))
        elif isinstance(keys,FstGrid):
            self.update(keys)
        else:
            raise TypeError,'FstGrid: wrong args in init; unrecognized grid desc'

    def interpol(self,fromData,fromGrid=None):
        """Interpolate (scalar) some gridded data to grid

        destData = myDestGrid.interpol(fromData,fromGrid)
        destRec  = myDestGrid.interpol(fromRec)

        Short for of calling:
        destData = myDestGrid.interpolVect(fromData,None,fromGrid)
        destRec  = myDestGrid.interpolVect(fromRec)

        See FstGrid.interpolVect() methode for documentation
        """
        return self.interpolVect(self,fromData,None,fromGrid)

    def interpolVect(self,fromDataX,fromDataY=None,fromGrid=None):
        """Interpolate some gridded scalar/vectorial data to grid

        (destDataX,destDataY) = myDestGrid.interpolVect(fromDataX,fromDataY,fromGrid)
        (destRecX,destRecY)   = myDestGrid.interpolVect(fromRecX,fromRecY)
        destDataX = myDestGrid.interpolVect(fromDataX,None,fromGrid)
        destRecX  = myDestGrid.interpolVect(fromRecX)

        @param fromDataX x-data to be interpolated (numpy.ndarray)
        @param fromDataY y-data to be interpolated (numpy.ndarray)
        @param fromGrid grid on which fromData is (FstGrid)
        @param fromRecX x-data+meta to be interpolated (FstRec)
        @param fromRecY y-data+meta to be interpolated (FstRec)
        @return destData interpolated data (numpy.ndarray)
        @return destRec interpolated data and update metadata (FstRec)
        @exception TypeError if args ar not of the right type
        @exception ValueError if problems with src grids
        """
        recx = None
        recy = None
        rectype = True
        if (type(fromDataX) == numpy.ndarray
            and isinstance(fromGrid,FstGrid)):
            rectype = False
            recx = FstRec()
            recx.d = fromDataX
            try:
                recx.setGrid(fromGrid)
            except:
                raise ValueError, 'FstGrid.interpolVect: fromGrid incompatible with fromDataX'
            if (type(fromDataY) == numpy.ndarray):
                recy = FstRec()
                recy.d = fromDataY
                try:
                    recy.setGrid(fromGrid)
                except:
                    raise ValueError, 'FstGrid.interpolVect: fromGrid incompatible with fromDataY'
            elif fromDataY:
                raise TypeError, 'FstGrid.interpolVect: fromDataY should be of same type as fromDataX'
        elif isinstance(fromDataX,FstRec):
            if fromGrid:
                raise TypeError, 'FstGrid.interpolVect: cannot provide both an FstRec for fromDataX and fromGrid'
            recx = fromDataX
            recx.setGrid()
            if isinstance(fromDataY,FstRec):
                recy = fromDataY
                recy.setGrid()
                if recx.grid != recy.grid:
                    raise ValueError, 'FstGrid.interpolVect: data X and Y should be on the same grid'
            elif fromDataY:
                raise TypeError, 'FstGrid.interpolVect: fromDataY should be of same type as fromDataX'
        else:
            raise TypeError, 'FstGrid.interpolVect: data should be of numpy.ndarray or FstRec type'
        sg = recx.grid
        dg = self
        sflag = (sg.xyaxis[0] != None)
        dflag = (dg.xyaxis[0] != None)
        vecteur = (recy != None)
        s_xyref = sg.ig14
        d_xyref = dg.ig14
        s_xyref.insert(0,sg.grtyp)
        d_xyref.insert(0,dg.grtyp)
        recyd = None
        if vecteur:
            recyd = recy.d
        dataxy = Fstdc.ezinterp(recx.d,recyd,
            sg.shape,sg.grtyp,s_xyref,sg.xyaxis[0],sg.xyaxis[1],sflag,
            dg.shape,dg.grtyp,d_xyref,dg.xyaxis[0],dg.xyaxis[1],dflag,vecteur)
        if rectype:
            recx.d = dataxy[0]
            recx.setGrid(self)
            if vecteur:
                recy.d = dataxy[1]
                recy.setGrid(self)
                return (recx,recy)
            else:
                return recx
        else:
            if vecteur:
                return (dataxy[0].d,dataxy[1].d)
            else:
                return dataxy[0].d


class FstRec(FstMeta):
    """Standard file record, with data (ndarray class) and full set of descriptors (FstMeta class)

    Example of use (and doctest tests):

    >>> r = FstRec()
    >>> r.d
    array([], dtype=float64)
    >>> r = FstRec([1,2,3,4])
    >>> r.d
    array([1, 2, 3, 4])
    >>> a = numpy.array([1,2,3,4],order='FORTRAN',dtype='float32')
    >>> r = FstRec(a)
    >>> r.d
    array([ 1.,  2.,  3.,  4.], dtype=float32)
    >>> a[1] = 5
    >>> r.d #r.d is a reference to a, thus changing a changes a
    array([ 1.,  5.,  3.,  4.], dtype=float32)
    >>> r = FstRec(a.copy())
    >>> r.d
    array([ 1.,  5.,  3.,  4.], dtype=float32)
    >>> a[1] = 9
    >>> r.d #r.d is a copy of a, thus changing a does not change a
    array([ 1.,  5.,  3.,  4.], dtype=float32)
    >>> r.grtyp
    'X'
    >>> r = FstRec([1,2,3,4])
    >>> r2 = FstRec(r)
    >>> d = r2.__dict__.items()
    >>> d.sort()
    >>> d
    [('d', array([1, 2, 3, 4])), ('dateo', 0), ('datev', -1), ('datyp', 0), ('deet', 0), ('etiket', '            '), ('fileref', None), ('grid', None), ('grtyp', 'X'), ('handle', -2), ('ig1', 0), ('ig2', 0), ('ig3', 0), ('ig4', 0), ('ip1', -1), ('ip2', -1), ('ip3', -1), ('nbits', 0), ('ni', -1), ('nj', -1), ('nk', -1), ('nom', '    '), ('npas', 0), ('nxt', 0), ('type', '  ')]
    >>> r.d[1] = 9 #r2 is a copy of r, thus this does not change r2.d
    >>> r2.d
    array([1, 2, 3, 4])

    @param data data part of the rec, can be a python list, numpy.ndarray or another FstRec
    @param params meta part of the record (FstMeta), if data is an FstRec it should not be provided
    @exceptions TypeError if arguments are not of valid type
    """
    def allowedKeysVals(self):
        """Return a dict of allowed Keys/Vals"""
        a = FstMeta.allowedKeysVals(self)
        a['d'] = None
        a['grid'] = None
        return a

    def __init__(self,data=None,params=None):
        FstMeta.__init__(self)
        if data == None:
            self.d = numpy.array([])
        elif type(data) == numpy.ndarray:
            self.d = data
        elif type(data) == type([]):
            self.d = numpy.array(data)
        elif isinstance(data,FstRec):
            if params:
                raise TypeError,'FstRec: cannot initialize with both an FstRec and params'
            self.d = data.d.copy()
            params = FstMeta(data)
        else:
            raise TypeError,'FstRec: cannot initialize data from arg #1'
        if params:
            if isinstance(params,FstMeta):
                self.update(params)
            elif type(params) == type({}):
                self.update_by_dict(params)
            else:
                raise TypeError,'FstRec: cannot initialize parameters from arg #2'

    def __setattr__(self,name,value):   # this method cannot create new attributes
        if name == 'd':
            if type(value) == numpy.ndarray:
                self.__dict__[name]=value
            else:
                raise TypeError,'FstRec: data should be an instance of numpy.ndarray'
        elif name == 'grid':
            if isinstance(value,FstGrid):
                self.__dict__[name]=value
            else:
                raise TypeError,'FstRec: grid should be an instance of FstGrid'
        else:
            FstMeta.__setattr__(self,name,value)

    def interpol(self,togrid):
        """Interpolate FstRec to another grid (horizontally)

        myFstRec.interpol(togrid)
        @param togrid grid where to interpolate
        @exception ValueError if myFstRec does not contain a valid grid desc
        @exception TypeError if togrid is not an instance of FstGrid
        """
        if isinstance(value,FstGrid):
            if not isinstance(self.grid,FstGrid):
                self.setGrid()
            if self.grid:
                self.d = togrid.interpol(self.d,self.grid)
                self.setGrid(togrid)
            else:
                raise ValueError,'FstRec.interpol(togrid): unable to determine actual grid of FstRec'
        else:
            raise TypeError,'FstRec.interpol(togrid): togrid should be an instance of FstGrid'

    def setGrid(self,newGrid=None):
        """Associate a grid to the FstRec (or try to get grid from rec metadata)

        myFstRec.setGrid()
        myFstRec.setGrid(newGrid)

        @param newGrid grid to associate to the record (FstGrid)
        @exception ValueError if newGrid does not have same shape as rec data or if it's impossible to determine grid params
        @exception TypeError if newGrid is not an FstGrid

        >>> r = FstRec([1,2,3,4],FstMeta())
        >>> g = FstGrid(grtyp='N',ig14=(1,2,3,4),ninj=(4,1))
        >>> (g.grtyp,g.shape,g.ig14)
        ('N', (4, 1), (1, 2, 3, 4))
        >>> r.setGrid(g)
        >>> (r.grtyp,(r.ni,r.nj),(r.ig1,r.ig2,r.ig3,r.ig4))
        ('N', (4, 1), (1, 2, 3, 4))
        >>> (r.grid.grtyp,r.grid.shape,r.grid.ig14)
        ('N', (4, 1), (1, 2, 3, 4))
        """
        if newGrid:
            if isinstance(newGrid,FstGrid):
                ni = max(self.d.shape[0],1)
                nj = 1
                if len(self.d.shape)>1:
                    nj = max(self.d.shape[1],1)
                if (ni,nj) != newGrid.shape:
                    raise ValueError,'FstRec.setGrid(newGrid): rec data and newGrid do not have the same shape'
                else :
                    self.grid = newGrid
                    self.grtyp = newGrid.grtyp
                    (self.ig1,self.ig2,self.ig3,self.ig4) = newGrid.ig14
                    (self.ni,self.nj) = newGrid.shape
            else:
                raise TypeError,'FstRec.setGrid(newGrid): newGrid should be an instance of FstGrid'
        else:
            self.grid = FstGrid(self)
            if self.grid:
                self.grtyp = self.grtyp
                (self.ig1,self.ig2,self.ig3,self.ig4) = self.ig14
                (self.ni,self.nj) = self.shape
            else:
                raise ValueError,'FstRec.setGrid(): unable to determine actual grid of FstRec'


class FstDate:
    """RPN STD Date representation

    myFstDate = FstDate(DATESTAMP)
    myFstDate = FstDate(YYYYMMDD,HHMMSShh)
    myFstDate = FstDate(myDateTime)
    myFstDate = FstDate(myFstMeta)
    @param DATESTAMP CMC date stamp or FstDate object
    @param YYYYMMDD  Int with Visual representation of YYYYMMDD
    @param HHMMSShh  Int with Visual representation of HHMMSShh
    @param myDateTime Instance of Python DateTime class
    @param myFstMeta Instance FstMeta with dateo,deet,npas properly set
    @exception TypeError if parameters are wrong type
    @exception ValueError if myFstMeta

    >>> d1 = FstDate(20030423,11453500)
    >>> d1
    FstDate(20030423,11453500)
    >>> d2 = FstDate(d1)
    >>> d2
    FstDate(20030423,11453500)
    >>> d2.incr(48)
    FstDate(20030425,11453500)
    >>> d1-d2
    -48.0
    >>> a = FstMeta(dateo=d1.stamp,deet=1800,npas=3)
    >>> d3 = FstDate(a)
    >>> d3
    FstDate(20030423,13153500)
    >>> utc = pytz.timezone("UTC")
    >>> d4 = datetime.datetime(2003,04,23,11,45,35,0,tzinfo=utc)
    >>> d5 = FstDate(d4)
    >>> d5
    FstDate(20030423,11453500)
    >>> d6 = d5.toDateTime()
    >>> d6 == d4
    True
    """
    stamp = 0

    def __init__(self,word1,word2=-1):
        if isinstance(word1,datetime.datetime):
            (yyyy,mo,dd,hh,mn,ss,dummy,dummy2,dummy3) = word1.utctimetuple()
            cs = int(word1.microsecond/10000)
            word1 = yyyy*10000+mo*100+dd
            word2 = hh*1000000+mn*10000+ss*100+cs
        if isinstance(word1,FstDate):
            self.stamp = word1.stamp
        elif isinstance(word1,FstMeta):
            if word1.deet<0 or word1.npas<0 or word1.dateo<=0 :
                raise ValueError, 'FstDate: Cannot compute date from FstMeta'
            nhours = (1.*word1.deet*word1.npas)/3600.
            self.stamp=Fstdc.incdatr(word1.dateo,nhours)

        elif type(word1) == type(0):    # integer type
            if (word2 == -1):
                self.stamp = word1
            else:
                dummy=0
                (self.stamp,dummy1,dummy2) = Fstdc.newdate(dummy,word1,word2,3)
        else:
            raise TypeError, 'FstDate: arguments should be of type int'

    def __sub__(self,other):
        "Time difference between 2 dates"
        return(Fstdc.difdatr(self.stamp,other.stamp))

    def incr(self,temps):
        """Increase Date by the specified number of hours

        @param temps Number of hours for the FstDate to be increased
        @return self

        @exception TypeError if temps is not of int or real type
        """
        if ((type(temps) == type(1)) or (type(temps) == type(1.0))):
            nhours = 0.0
            nhours = temps
            self.stamp=Fstdc.incdatr(self.stamp,nhours)
            return(self)
        else:
            raise TypeError,'FstDate.incr: argument should be int or real'

    def toDateTime(self):
        """Return the DateTime obj representing the FstDate

        >>> myFstDate = FstDate(20030423,11453600)
        >>> myDateTime = myFstDate.toDateTime()
        >>> myDateTime
        datetime.datetime(2003, 4, 23, 11, 45, 35, tzinfo=<UTC>)

        #TODO: oups 1 sec diff!!!
        """
        word1 = word2 = 0
        (dummy,word1,word2) = Fstdc.newdate(self.stamp,word1,word2,-3)
        d = "%8.8d.%8.8d" % (word1, word2)
        yyyy = int(d[0:4])
        mo = int(d[4:6])
        dd = int(d[6:8])
        hh = int(d[9:11])
        mn = int(d[11:13])
        ss = int(d[13:15])
        cs = int(d[15:17])
        utc = pytz.timezone("UTC")
        return datetime.datetime(yyyy,mo,dd,hh,mn,ss,cs*10000,tzinfo=utc)

    def __repr__(self):
        word1 = word2 = 0
        (dummy,word1,word2) = Fstdc.newdate(self.stamp,word1,word2,-3)
        return "FstDate(%8.8d,%8.8d)" % (word1, word2)


class FstDateRange:
    """RPN STD Date Range representation

    FstDateRange(DateStart,DateEnd,Delta)
    @param DateStart FstDate start of the range
    @param DateEnd   FstDate end of the range
    @param Delta     Increment of the range iterator, hours, real

    @exception TypeError if parameters are wrong type

    >>> d1 = FstDate(20030423,11453500)
    >>> d2 = FstDate(d1)
    >>> d2.incr(48)
    FstDate(20030425,11453500)
    >>> dr = FstDateRange(d1,d2,6)
    >>> dr
    FstDateRage(from:(20030423,11453500), to:(20030425,11453500), delta:6) at (20030423,11453500)
    >>> dr.lenght()
    48.0
    >>> dr.next()
    FstDate(20030423,17453500)
    >>> dr = FstDateRange(d1,d2,36)
    >>> dr
    FstDateRage(from:(20030423,17453500), to:(20030425,11453500), delta:36) at (20030423,17453500)
    >>> dr.next()
    FstDate(20030425,05453500)
    >>> dr.next() #returns None because it is past the end of DateRange
    """
    #TODO: make this an iterator
    dateDebut=-1
    dateFin=-1
    delta=0.0
    now=-1

    def __init__(self,debut=-1,fin=-1,delta=0.0):
        if isinstance(debut,FstDate) and isinstance(fin,FstDate) and ((type(delta) == type(1)) or (type(delta) == type(1.0))):
            self.dateDebut=debut
            self.now=debut
            self.dateFin=fin
            self.delta=delta
        else:
            raise TypeError,'FstDateRange: arguments type error FstDateRange(FstDate,FstDate,Real)'

    def lenght(self):
        """Provide the duration of the date range
        @return Number of hours
        """
        return abs(self.dateFin-self.dateDebut)

    def remains():
        """Provide the number of hours left in the date range
        @return Number of hours left in the range
        """
        return abs(self.dateFin-self.now)

    def next(self):
        """Return the next date/time in the range (step of delta hours)
        @return next FstDate, None if next date is beyond range
        """
        self.now.incr(self.delta)
        if (self.dateFin-self.now)*self.delta < 0.:
            return None
        return FstDate(self.now)

    def reset(self):
        """Reset the FstDateRange iterator to the range start date"""
        self.now=self.dateDebut

    def __repr__(self):
        d1 = repr(self.dateDebut)
        d2 = repr(self.dateFin)
        d0 = repr(self.now)
        return "FstDateRage(from:%s, to:%s, delta:%d) at %s" % (d1[7:27],d2[7:27],self.delta,d0[7:27])


class FstMapDesc:
    "Map Descriptors with lat1,lon1, lat2,lon2, rot"
    def __init__(self,key,xs1=0.,ys1=0.,xs2=0.,ys2=0.,ni=0,nj=0):
        print 'Debug FstMapDesc grtyp ig1-4=',key.grtyp,key.ig1,key.ig2,key.ig3,key.ig4
#        print 'Debug FstMapDesc xs1,ys1,xs2,ys2=',xs1,ys1,xs2,ys2
        if isinstance(key,FstParm):
          print 'Debug FstMapDesc appel a Fstdc.mapdscrpt'
          print 'xs1,ys1,xs2,ys2=',xs1,ys1,xs2,ys2
          self.geodesc=Fstdc.mapdscrpt(xs1,ys1,xs2,ys2,ni,nj,key.grtyp,key.ig1,key.ig2,key.ig3,key.ig4)
#       (self.lat1,self.lon1,self.lat2,self.lon2,self.rot)=Fstdc.mapdscrpt(xs1,ys1,xs2,ys2,key.grtyp,key.ig1,key.ig2,key.ig3,key.ig4)
        else:
            raise TypeError,'FstMapdesc: invalid key'

FirstRecord=FstMeta()
NextMatch=None
Predef_Grids()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
