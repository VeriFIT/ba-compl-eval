#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <spot/twa/twagraph.hh>
#include <spot/parseaut/public.hh>
#include <cstring>

// Parse a pair of automata file paths from a line
bool parse_line(const std::string& line, std::string& file1, std::string& file2)
{
  size_t pos = line.find(';');
  if (pos == std::string::npos)
    return false;
  
  file1 = line.substr(0, pos);
  file2 = line.substr(pos + 1);
  
  // Trim whitespace
  file1.erase(0, file1.find_first_not_of(" \t\r\n"));
  file1.erase(file1.find_last_not_of(" \t\r\n") + 1);
  file2.erase(0, file2.find_first_not_of(" \t\r\n"));
  file2.erase(file2.find_last_not_of(" \t\r\n") + 1);
  
  return !file1.empty() && !file2.empty();
}

// Load an automaton from a file
spot::twa_graph_ptr load_automaton(const std::string& filename, spot::bdd_dict_ptr dict)
{
  spot::parsed_aut_ptr pa = parse_aut(filename, dict);
  if (pa->format_errors(std::cerr))
    {
      std::cerr << "Error parsing file: " << filename << '\n';
      return nullptr;
    }
  if (pa->aborted)
    {
      std::cerr << "Aborted reading file: " << filename << '\n';
      return nullptr;
    }
  return pa->aut;
}

int main(int argc, const char** argv)
{
  // Help option
  if (argc >= 2 && (!std::strcmp(argv[1], "-h") || !std::strcmp(argv[1], "--help")))
    {
      std::cout << "check_ap - Atomic Propositions Checker\n\n";
      std::cout << "Verify that each pair of HOA automata listed in an input file\n";
      std::cout << "has the same number of atomic propositions (APs).\n\n";
      std::cout << "Usage:\n  " << argv[0] << " <input-file>\n\n";
      std::cout << "Input format (one pair per line, semicolon-separated; '#' for comments):\n";
      std::cout << "  path/to/A.hoa;path/to/B.hoa\n\n";
      std::cout << "Output:\n";
      std::cout << "  - For each pair: reports whether AP counts match or not.\n";
      std::cout << "  - Summary with totals at the end.\n\n";
      std::cout << "Exit code: 0 if all pairs match; 1 otherwise.\n";
      return 0;
    }

  if (argc != 2)
    {
      std::cerr << "Usage: " << argv[0] << " <input-file>\n";
      std::cerr << "Input file should contain pairs of automaton paths separated by semicolons,\n";
      std::cerr << "one pair per line.\n";
      return 1;
    }

  std::ifstream input_file(argv[1]);
  if (!input_file)
    {
      std::cerr << "Cannot open input file: " << argv[1] << '\n';
      return 1;
    }

  // Create a shared BDD dictionary for all automata
  spot::bdd_dict_ptr dict = spot::make_bdd_dict();
  
  std::string line;
  int line_number = 0;
  int mismatches = 0;
  int total_pairs = 0;
  
  while (std::getline(input_file, line))
    {
      line_number++;
      
      // Skip empty lines and comments
      if (line.empty() || line[0] == '#')
        continue;
      
      std::string file1, file2;
      if (!parse_line(line, file1, file2))
        {
          std::cerr << "Warning: Line " << line_number << " has invalid format, skipping\n";
          continue;
        }
      
      total_pairs++;
      
      // Load both automata
      spot::twa_graph_ptr aut1 = load_automaton(file1, dict);
      spot::twa_graph_ptr aut2 = load_automaton(file2, dict);
      
      if (!aut1 || !aut2)
        {
          std::cerr << "Error loading automata on line " << line_number << ", skipping\n";
          continue;
        }
      
      // Get the number of atomic propositions
      unsigned ap1 = aut1->ap().size();
      unsigned ap2 = aut2->ap().size();
      
      // Check if they match
      if (ap1 != ap2)
        {
          mismatches++;
          std::cout << "MISMATCH on line " << line_number << ":\n";
          std::cout << "  File 1: " << file1 << " (APs: " << ap1 << ")\n";
          std::cout << "  File 2: " << file2 << " (APs: " << ap2 << ")\n";
        }
      else
        {
          std::cout << "OK on line " << line_number << ": " << ap1 << " APs match\n";
        }
    }
  
  std::cout << "\n=== Summary ===\n";
  std::cout << "Total pairs checked: " << total_pairs << '\n';
  std::cout << "Matching pairs: " << (total_pairs - mismatches) << '\n';
  std::cout << "Mismatching pairs: " << mismatches << '\n';
  
  return (mismatches > 0) ? 1 : 0;
}
