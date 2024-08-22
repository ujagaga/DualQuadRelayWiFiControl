#ifndef PINCTRL_H
#define PINCTRL_H

extern void PINCTRL_write(int pinId, int state);
extern int PINCTRL_getCurrentVal( int pinId );
extern void PINCTRL_init(void);

#endif
