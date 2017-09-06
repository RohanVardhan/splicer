"""
Copyright PyXLL Ltd
www.pyxll.com

PyXLL allows you to create Excel addins written in Python.

*************************************************************************
* IMPORTANT:                                                            *
*  This module is NOT the actual pyxll module used when your PyXLL      *
*  addin runs in Excel.                                                 *
*                                                                       *
*  It is just a module of stubs functions so that you can import pyxll  *
*  from other python interpreters outside of Excel (for unit testing,   *
*  for example).                                                        *
*************************************************************************

This module contains decorators used by the PyXLL Excel addin to expose
python functions as worksheet functions, macro functions and menu items
to Excel.

For full documentation please refer to www.pyxll.com.
"""
try:
    import threading
    _have_threading = True
except ImportError:
    # create a fake threading module that will only fail
    # when a thread is created
    class threading:
        class Thread:
            def __init__(self, *args, **kwargs):
                raise Exception("threading module not found")
    _have_threading = False

nan = 1e10000 * 0

xlCalculationAutomatic = 1
xlCalculationSemiAutomatic = 2
xlCalculationManual = 3

xlDialogTypeNone = 0
xlDialogTypeFunctionWizard = 1
xlDialogTypeSearchAndReplace = 2

def get_active_object():
    """
    Return the Excel Window corresponding to the Excel application
    the PyXLL addin is running in.
    
    When called from outside of Excel, this will return the first
    open Excel window found. If there is no Excel window open,
    this function will raise and Exception.
    """
    # this is only used when calling from outside Excel.
    # the builtin pyxll module does 'the right thing'.
    import win32com.client
    xl = win32com.client.Dispatch("Excel.Application")
    return xl.Windows[0]

def get_dialog_type():
    """
    Returns a value indicating what type of dialog a function was
    called from, if any.
    
    This can be used to disable slow running calculations in the
    function wizard or when doing a search and replace operation.
    """
    return xlDialogTypeNone

def xlfGetDocument(arg_num, name=None):
    raise Exception("Not supported when running outside of Excel")

def xlfGetWorkspace(arg_num):
    raise Exception("Not supported when running outside of Excel")

def xlfGetWorkbook(arg_num, workbook_name=None):
    raise Exception("Not supported when running outside of Excel")
    
def xlfGetWindow(arg_num, workbook_name=None):
    raise Exception("Not supported when running outside of Excel")

def xlfWindows(match_type=None, mask=None):
    raise Exception("Not supported when running outside of Excel")

def xlfCaller():
    raise Exception("Not supported when running outside of Excel")

def xlAsyncReturn(async_handle, value):
    raise Exception("Not supported when running outside of Excel")

def xlcAlert(message):
    raise Exception("Not supported when running outside of Excel")

def xlcCalculation(calculation_type):
    raise Exception("Not supported when running outside of Excel")

def xlcCalculateNow():
    raise Exception("Not supported when running outside of Excel")

def xlcCalculateDocument():
    raise Exception("Not supported when running outside of Excel")

def xlAbort(retain=True):
    raise Exception("Not supported when running outside of Excel")

class XLAsyncHandle(object):
    def __init__(self, *args, **kwargs):
        assert Exception("Not supported when running outside of Excel")

class XLCell(object):
    def __init__(self, *args, **kwargs):
        assert Exception("Not supported when running outside of Excel")

def get_config():
    """returns the PyXLL config as a ConfigParser.SafeConfigParser instance"""
    raise Exception("Not supported when running outside of Excel")

def xl_version():
    """
    returns the version of Excel the addin is running in as a float.

    8.0  => Excel 97
    9.0  => Excel 2000
    10.0 => Excel 2002
    11.0 => Excel 2003
    12.0 => Excel 2007
    14.0 => Excel 2010
    """
    raise Exception("Not supported when running outside of Excel")

def xl_func(signature,
            category="PyXLL",
            shortcut_text="",
            help_topic="",
            thread_safe=False,
            macro=False,
            volatile=False,
            disable_function_wizard_calc=False,
            disable_replace_calc=False,
            arg_descriptions=None):
    """
    Decorator for exposing functions to excel.

    eg:
    @xl_func("string a, int b, float c: string")
    def my_xl_function(a, b, c)
        '''docstrings appear as helptext in excel'''
        return "%s %d %f" % (a, b, c)

    Valid types are:
        str, string, int, bool, float, float[], var or types registered
        with xl_arg_type.

    The return type is optional, it will default to var.
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_arg_doc(arg_name, docstring):
    """
    Decorator for documenting a function's named parameters.
    Must be applied before xl_func.
    
    eg:

    @xl_func("int a, int b: int")
    @xl_arg_doc("a", "this is the docstring for a")
    @xl_arg_doc("b", "this is the docstring for b")
    def my_xl_function(a, b):
        return a + b

    Alternatively if no docstrings are explicitly supplied
    and the function has a docstring, PyXLL will try and
    find parameter documentation in the docstring.

    @xl_func("int a, int b: int")
    def my_xl_function(a, b):
        '''
        return a + b

        a : this is the docstring for a
        b : this is the docstring for b
        '''
        return a + b

    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_macro(signature="", arg_descriptions=None):
    """
    Decorator for exposing python functions as macros.
    
    Macros are used like VBA macros and can be assigned to buttons.
    They take no arguments the return value is not used.
    
    Macros may call macro sheet functions and may call back
    into Excel like menu items.
    
    eg:
    @xl_macro()
    def my_macro():
        win32api.MessageBox(0, "my_macro", "my_macro")
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_arg_type(name, base_type, allow_arrays=True, macro=None,thread_safe=None):
    """
    Decorator for adding custom types for use with
    functions exposed via xl_func and xl_macro.
    eg:
    
    class myobject:
        def __init__(self, name):
            self.name = name

    @xl_arg_type("myobject", "string")
    def myobject_from_string(name):
        return myobject(name)
        
    @xl_func("myobject obj: string")
    def get_name(obj):
        return obj.name

    in this example, get_name is called from excel with a string argument
    that is converted to a myobject instance via myobject_from_string.

    If allow_arrays is True, arrays of the custom type are allowed
    using the standard signature notation 'myobject[]' (for the example
    above).
    
    macro and thread_safe can be set if the function using this type
    must be a macro equivalent function (set macro=True) or must not
    be registered as thread safe (set thread_safe=False).
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_return_type(name, base_type, allow_arrays=True, macro=None, thread_safe=None):
    """
    Decorator for adding custom types for use with
    functions exposed via xl_func and xl_macro.
    eg:
    
    class myobject:
        def __init__(self, name):
            self.name = name
            
    @xl_return_type("myobject", "string")
    def myobject_to_string(obj):
        return obj.name
    
    @xl_func("string name: myobject")
    def get_object(name):
        return myobject(name)
    
    in this example, get_object is called from excel with a string
    argument and returns a myobject instance. That is converted to a
    string by the registered myobject_to_string function and returned
    to excel as a string.
    
    If allow_arrays is True, arrays of the custom type are allowed
    using the standard signature notation 'myobject[]' (for the example
    above).

    macro and thread_safe can be set if the function using this type
    must be a macro equivalent function (set macro=True) or must not
    be registered as thread safe (set thread_safe=False).
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_menu(name, menu=None, sub_menu=None, order=None, sub_order=None, menu_order=None):
    """
    Decorator for creating custom menu items.
    
    eg.
    
    @xl_menu("My menu item")
    def my_menu_item():
        print "my menu item was called"
        
    Adds a menu item 'My menu item' to the default menu (PyXLL or addin
    name).
    
    @xl_menu("My menu item", menu="My Menu")
    def my_menu_item():
        print "my menu item was called"
        
    Creates a new menu "My Menu" and adds "My menu item" to it.

    @xl_menu("Mysub-menu item", menu="My Menu", sub_menu="My Sub Menu")
    def my_menu_item():
        print "my menu item was called"
    
    Creates a new sub-menu "My Sub Menu" and adds "My sub-menu item"
    to it.
    If the menu My Menu didn't already exist, it would create it too.
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_license_notifier(func):
    """
    Decorator for callbacks to notify user code of the current state of
    the license.
    
    The decorated function must be of the form:
    def callback(string name, datetime.date expdate, int days_left, bool is_perpetual)
    
    All registered callbacks are called only once when the license is
    checked at the time pyxll is first loaded.

    If the license is perpetual, expdate will be end date of the maintenance contract
    and days_left will be the days between the pyxll build date and expdate.
    """
    return func

def xl_on_close(func):
    """
    Decorator for callbacks that should be called when Excel is about
    to be closed.
    
    Even after this function has been called, it's possible Excel won't
    actually close as the user may veto it.
    
    The function should take no arguments.
    """
    return func

def xl_on_reload(func):
    """
    Decorator for callbacks that should be called after a reload is
    attempted.
    
    The callback takes a list of tuples of three three items:
    (modulename, module, exc_info)
    
    When a module has been loaded successfully, exc_info is None.
    When a module has failed to load, module is None and exc_info
    is the exception information (exc_type, exc_value, exc_traceback).
    """
    return func

def xl_on_open(func):
    """
    Decorator for callbacks that should be called after PyXLL has
    been opened and the user modules have been imported.
    
    The callback takes a list of tuples of three three items:
    (modulename, module, exc_info)
    
    When a module has been loaded successfully, exc_info is None.
    When a module has failed to load, module is None and exc_info
    is the exception information (exc_type, exc_value, exc_traceback).
    """
    return func

win32com = None
pythoncom = None
def _import_com(pythoncom_only=False):
    """lazily import win32com and pythoncom as not all apps will need it"""
    global win32com, pythoncom
    try:
        if not pythoncom_only and win32com is None:
            import win32com.client
            import win32com as win32com_module
            win32com = win32com_module
        if pythoncom is None:
            import pythoncom as pythoncom_module
            pythoncom = pythoncom_module
    except ImportError:
        return False
    return True

class AsyncFunctionThread(threading.Thread):
    """
    a thread class for calling callable objects in a background thread
    """
    class ComMarshaler:
        def __init__(self, obj):
            if isinstance(obj, win32com.client.DispatchBaseClass) \
            or isinstance(obj, win32com.client.CoClassBaseClass) \
            or isinstance(obj, win32com.client.EventsProxy) \
            or isinstance(obj, win32com.client.CDispatch):
                self.__iswrapped = True
                self.__stream = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, obj._oleobj_)
            else:
                self.__iswrapped = False
                self.__stream = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, obj)

        def get_dispatch(self):
            obj = pythoncom.CoGetInterfaceAndReleaseStream(self.__stream, pythoncom.IID_IDispatch)
            self.____stream = None
            if self.__iswrapped:
                obj = win32com.client.Dispatch(obj)
            return obj

    class JobAdderTimerCallback:
        def __init__(self, async_obj, func, args, kwargs):
            self.async_obj = async_obj
            self.func = func
            self.args = args
            self.kwargs = kwargs

        def __call__(self, timer_id, time):
            # we only want to be called once
            self.async_obj.kill_timer(timer_id)

            # check if any of the arguments need marshalling
            unmarshal = False
            if _import_com():
                args = list(self.args)
                for i, arg in enumerate(args):
                    if isinstance(arg, win32com.client.DispatchBaseClass) \
                    or isinstance(arg, win32com.client.CoClassBaseClass) \
                    or isinstance(arg, win32com.client.EventsProxy) \
                    or isinstance(arg, win32com.client.CDispatch) \
                    or isinstance(arg, pythoncom.TypeIIDs[pythoncom.IID_IDispatch]):
                        args[i] = self.async_obj.ComMarshaler(arg)
                        unmarshal = True
                self.args = tuple(args)

                kwargs = dict(self.kwargs)
                for key, arg in kwargs.items():
                    if isinstance(arg, win32com.client.DispatchBaseClass) \
                    or isinstance(arg, win32com.client.CoClassBaseClass) \
                    or isinstance(arg, win32com.client.EventsProxy) \
                    or isinstance(arg, win32com.client.CDispatch) \
                    or isinstance(arg, pythoncom.TypeIIDs[pythoncom.IID_IDispatch]):
                        kwargs[key] = self.async_obj.ComMarshaler(arg)
                        unmarshal = True
                self.kwargs = kwargs

            # add the job to the queue
            self.async_obj._condition.acquire()
            if self.async_obj._running:
                self.async_obj._jobs.append((self.func, self.args, self.kwargs, unmarshal))
                self.async_obj._condition.notify()
            self.async_obj._condition.release()

            self.async_object = self.args = self.kwargs = self.func = None

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.setDaemon(True)
        self._condition = threading.Condition()
        self._running = False
        self._jobs = []

        # the timer module is used to add jobs to the queue in the windows message loop
        try:
            import timer
            self.set_timer = timer.set_timer
            self.kill_timer = timer.kill_timer
        except ImportError:
            _log.warn("pywin32 timer module not found; using async_call and COM objects together may cause deadlocks")
            self.set_timer = lambda x, func: func(0, 0)
            self.kill_timer = lambda timer_id: None

    def run(self):
        if _import_com(True):
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
        try:
            while self._running:
                # get the next job
                self._condition.acquire()
                while not self._jobs and self._running:
                    self._condition.wait()
                if not self._running:
                    return
                func, args, kwargs, unmarshal = self._jobs.pop(0)
                self._condition.release()

                try:
                    # unmarshal any com objects
                    if unmarshal:
                        args = list(args)
                        for i, arg in enumerate(args):
                            if isinstance(arg, self.ComMarshaler):
                                args[i] = arg.get_dispatch()
                        args = tuple(args)
                        kwargs = dict(kwargs)
                        for key, arg in kwargs.items():
                            if isinstance(arg, self.ComMarshaler):
                                kwargs[key] = arg.get_dispatch()

                    # try calling it
                    func(*args, **kwargs)
                except Exception as e:
                    traceback.print_exc(file=sys.stderr)

        finally:
            if pythoncom:
                pythoncom.CoUninitialize()

    def async_call(self, func, *args, **kwargs):
        """call a callable object in the background thread"""
        self.set_timer(0, self.JobAdderTimerCallback(self, func, args, kwargs))

    def start(self):
        self._running = True
        threading.Thread.start(self)

    def stop(self):
        if self._running:
            self._condition.acquire()
            self._jobs = []
            self._running = False
            self._condition.notify()
            self._condition.release()
        return not self._running

    def __del__(self):
        self.stop()

_async_function_thread = None
def async_call(func, *args, **kwargs):
    """
    Call a function asyncronously from a background thread.
    
    Additional arguments and keyword arguments will be passed to the
    function.
    
    This can be used for macro functions that modify the worksheet, where
    calling back into Excel from the main thread would cause a deadlock.
    
    If called from a macro function, the background thread will block
    until the macro function has returned.
    """
    if not _have_threading:
        raise Exception("threading module not available")

    if __pyxll_py_threads_disabled__:
        raise Exception("Python threads have not been initialized")

    # start the async function call thread if necessary
    global _async_function_thread
    if _async_function_thread is None:
        _async_function_thread = AsyncFunctionThread(name="PyXLL AsyncFunctionThread")
        _async_function_thread.start()

    # add the function to the async function thread's call list
    _async_function_thread.async_call(func, *args, **kwargs)