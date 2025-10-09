CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -MMD -MP

# Simple, overridable include/lib locations (tune these if your Spot install lives elsewhere)
INCDIR ?= /usr/local/include
LIBDIR ?= /usr/local/lib

CPPFLAGS ?= -I$(INCDIR)
LDFLAGS  ?= -L$(LIBDIR)
LIBS     ?= -lspot -lbddx

SRCS = hoaba.cpp check_ap.cpp
OBJS = $(SRCS:.cpp=.o)
DEPS = $(OBJS:.o=.d)
TARGETS = hoaba check_ap

.PHONY: all clean

all: $(TARGETS)

# Explicit build rules for the two binaries
hoaba: hoaba.o
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

check_ap: check_ap.o
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

# Compile object files
%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(DEPS) $(TARGETS)

-include $(DEPS)
