# Büchi automata complementation evalution environment

## Installing Dependencies
```
cd bench
pip3 install -r requirements.txt
```

## Installing Other Tools

This section describes how to install other tools.  You can also turn tools off by commenting the appropriate line in `bench/ba-compl.yaml`.

The instructions assume that this repository is located in `${HOME}/ba-compl-eval`.

### GOAL

Download [GOAL](http://goal.im.ntu.edu.tw/wiki/doku.php#download) and move the file into the `bin/` directory.  Then

```
cd bin/
unzip GOAL-xxxxxxxx.zip
mv GOAL-xxxxxxxx/ goal/
```

#### MacOS
After installing GOAL, copy the GOAL directory:
```
cp -r /Applications/GOAL.app/Contents/Resources/Java bin/goal
```

### Spot

We compile Spot and copy the file `autfilt` and the required libraries into the `bin/` directory

```
cd bin/
wget http://www.lrde.epita.fr/dload/spot/spot-2.9.3.tar.gz
tar xzf spot-2.9.3.tar.gz
cd spot-2.9.3/
./configure
make
cp bin/autfilt ../
cp spot/.libs/libspot.so.0 ../
cp buddy/src/.libs/libbddx.so.0 ../
export LD_LIBRARY_PATH=$HOME/ba-compl-eval/bin        # or the correct path
```

#### MacOS
On MacOS, you may need to change `$BISON` to point to non-system installation of Bison.

### Seminator 2

It is necessary to install Spot before installing Seminator 2.

```
cd bin/
wget https://github.com/mklokocka/seminator/releases/download/v2.0/seminator-2.0.tar.gz
tar xzvf seminator-2.0.tar.gz
cd seminator-2.0/

SPOT="${HOME}/ba-compl-eval/bin/spot-2.9.3"   # or the path to sources of Spot
./configure CXXFLAGS="-I${SPOT} -I${SPOT}/buddy/src" LDFLAGS="-L${SPOT}/spot/.libs -L${SPOT}/buddy/src/.libs"
make
cp .libs/seminator ../
cp src/.libs/libseminator.so.0 ../
```

### ROLL

```
wget 'https://github.com/ISCAS-PMC/roll-library/archive/dev.tar.gz' -O roll.tar.gz
tar xzvf roll.tar.gz
cd roll-library-dev/
./build.sh
cp ROLL.jar ../
```

### Ranker

```
wget 'https://github.com/vhavlena/ba-inclusion/archive/master.tar.gz' -O ranker.tar.gz
tar xzvf ranker.tar.gz
cd ba-inclusion-master/src/
make
cp rnk-red-complement ../../ranker
```


TODO: RABIT

Ranker internally uses RABIT, for running it, you may need a particular version of Java installed.

```
export RABITEXE="${HOME}/ba-compl-eval/bin/rabit/RABIT.jar" # or the correct path
```

## Running Experiments

```
export LD_LIBRARY_PATH=$HOME/ba-compl-eval/bin              # or the correct path
export RABITEXE="${HOME}/ba-compl-eval/bin/rabit/RABIT.jar" # or the correct path
```