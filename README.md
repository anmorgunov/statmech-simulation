# Simulator

Please see the [report](report/main.pdf) for a description of the project

## To-do list

### Potential optimizations

- [ ] Recalculate number of particles in left and right compartment inside of move method (reduce O(2n) to O(n))
- [x] Grid for collision checks
- [ ] Right now you check if you collide with the wall, and if you do, you revert velocity. Make sure you don't step into the wall as well.

## Acknowledgements

- Periodic table parsed into a JSON format was taken from [Bowserinator/Periodic-Table-JSON](https://github.com/Bowserinator/Periodic-Table-JSON)
