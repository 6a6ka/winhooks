from collections import namedtuple


handlers = []
KeyboardEvent = namedtuple('KeyboardEvent', ['event_type', 'key_code',
                                             'scan_code', 'alt_pressed',
                                             'time'])


def print_event(e):
	print(e)


def listen():
	from ctypes import windll, CFUNCTYPE, POINTER, c_int, c_void_p, byref
	import atexit

	event_types = {
		0x0100: 'key down',
		0x0101: 'key up',
		0x104: 'key down',  # WM_SYSKEYDOWN, used for Alt key.
		0x105: 'key up',  # WM_SYSKEYUP, used for Alt key.
	}

	def low_level_handler(nCode, wParam, lParam):
		"""
		Processes a low level Windows keyboard event.
		"""
		event = KeyboardEvent(event_types[wParam], lParam[0], lParam[1],
							lParam[2] == 32, lParam[3])
		for handler in handlers:
			handler(event)

		return windll.user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

	# Our low level handler signature.
	CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
	# Convert the Python handler into C pointer.
	pointer = CMPFUNC(low_level_handler)

	# Hook both key up and key down events for common keys (non-system).
	# 13 for WH_KEYBOARD_LL - https://msdn.microsoft.com/en-us/library/windows/desktop/ms644990%28v=vs.85%29.aspx
	hook_id = windll.user32.SetWindowsHookExA(13, pointer,
											 windll.kernel32.GetModuleHandleA(None), 0)

	# Register to remove the hook when the interpreter exits.
	atexit.register(windll.user32.UnhookWindowsHookEx, hook_id)

	while True:
		msg = windll.user32.GetMessageW(None, 0, 0, 0)
		windll.user32.TranslateMessage(byref(msg))
		windll.user32.DispatchMessageW(byref(msg))


if __name__ == '__main__':
	handlers.append(print_event)
	listen()
