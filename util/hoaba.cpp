#include <iostream>
#include <fstream>
#include <sstream>
#include <map>
#include <set>
#include <spot/twa/twagraph.hh>
#include <spot/twaalgos/sbacc.hh>
#include <spot/twaalgos/split.hh>
#include <spot/parseaut/public.hh>
#include <cstring>

// Prepare automaton: convert to state-based acceptance and split edges
spot::twa_graph_ptr prepare_automaton(spot::twa_graph_ptr aut)
{
  // The input should have Büchi acceptance.  Alternatively,
  // allow "t" acceptance since we can interpret this as a Büchi automaton
  // where all states are accepting.
  const spot::acc_cond& acc = aut->acc();
  if (!(acc.is_buchi() || acc.is_t()))
    throw std::runtime_error("unsupported acceptance condition");

  // The BA format only support state-based acceptance, so get rid
  // of transition-based acceptance if we have some.
  aut = spot::sbacc(aut);

  // We want one minterm per edge, as those will become letters
  aut = spot::split_edges(aut);

  return aut;
}

// Collect all conditions from an automaton
std::map<std::string, bdd> collect_conditions(spot::twa_graph_ptr aut)
{
  std::map<std::string, bdd> conditions;
  for (auto& e: aut->edges())
  {
    std::ostringstream oss;
    oss << e.cond;
    std::string cond_str = oss.str();
    conditions[cond_str] = e.cond;
  }
  return conditions;
}

// Create a unified mapping from BDD conditions to integers
// Returns a map from bdd string representation to the assigned integer
std::map<std::string, unsigned> create_condition_mapping(
    const std::map<std::string, bdd>& conds1, 
    const std::map<std::string, bdd>& conds2)
{
  std::map<std::string, unsigned> cond_str_to_int;
  std::map<std::string, bdd> all_conds;
  
  // Merge both condition maps
  all_conds.insert(conds1.begin(), conds1.end());
  all_conds.insert(conds2.begin(), conds2.end());
  
  // Assign sequential integers to each unique condition
  unsigned counter = 0;
  for (const auto& pair : all_conds)
  {
    cond_str_to_int[pair.first] = counter++;
  }
  
  return cond_str_to_int;
}

// Print automaton in BA format using the provided condition mapping
void print_ba_format(std::ostream& out, spot::twa_graph_ptr aut, 
                     const std::map<std::string, unsigned>& cond_str_to_int)
{
  const spot::acc_cond& acc = aut->acc();
  
  out << aut->get_init_state_number() << '\n';
  for (auto& e: aut->edges())
  {
    std::ostringstream oss;
    oss << e.cond;
    std::string cond_str = oss.str();
    auto it = cond_str_to_int.find(cond_str);
    if (it == cond_str_to_int.end())
      throw std::runtime_error("condition not found in mapping");
    out << it->second << ',' << e.src << "->" << e.dst << '\n';
  }

  unsigned ns = aut->num_states();
  for (unsigned s = 0; s < ns; ++s)
    if (acc.accepting(aut->state_acc_sets(s)))
       out << s << '\n';
}

// Print the condition to integer mapping
void print_condition_mapping(std::ostream& out, 
                             const std::map<std::string, bdd>& cond_str_to_bdd,
                             const std::map<std::string, unsigned>& cond_str_to_int)
{
  out << "Condition to Integer mapping:\n";
  for (const auto& pair : cond_str_to_int)
  {
    const std::string& cond_str = pair.first;
    unsigned mapped_int = pair.second;
    auto it = cond_str_to_bdd.find(cond_str);
    if (it != cond_str_to_bdd.end())
    {
      out << "Integer: " << mapped_int << " -> Condition: " << it->second << '\n';
    }
  }
  out << '\n';
}

int main(int argc, const char** argv)
{
  // Help option
  if (argc >= 2 && (!std::strcmp(argv[1], "-h") || !std::strcmp(argv[1], "--help")))
    {
      std::cout << "hoaba - Dual Automaton Converter\n\n";
      std::cout << "Convert two HOA automata to BA format with a unified condition mapping.\n";
      std::cout << "This ensures identical conditions across both automata share the same integer label.\n\n";
      std::cout << "Usage:\n  " << argv[0] << " <input1.hoa> <input2.hoa>\n\n";
      std::cout << "Outputs:\n";
      std::cout << "  <input1>.ba  - first automaton in BA format\n";
      std::cout << "  <input2>.ba  - second automaton in BA format\n";
      std::cout << "Details:\n";
      std::cout << "- Splits edges so each edge has a single minterm (Spot split_edges).\n";
      std::cout << "- Converts to state-based acceptance (Spot sbacc).\n";
      std::cout << "- Builds a unified mapping from condition strings to integers across both inputs.\n";
      return 0;
    }

  if (argc != 3)
    {
      std::cerr << "Usage: " << argv[0] << " <input1.hoa> <input2.hoa>\n";
      std::cerr << "Converts two HOA automata to BA format with unified condition mapping\n";
      std::cerr << "Output files: <input1>.ba and <input2>.ba\n";
      std::cerr << "Mapping file: <input1>_<input2>.mapping\n";
      return 1;
    }
  
  const char* filename1 = argv[1];
  const char* filename2 = argv[2];
  
  // Create a shared BDD dictionary for both automata
  spot::bdd_dict_ptr dict = spot::make_bdd_dict();
  
  // Parse first automaton
  spot::parsed_aut_ptr pa1 = parse_aut(filename1, dict);
  if (pa1->format_errors(std::cerr))
    {
      std::cerr << "Error parsing first automaton: " << filename1 << '\n';
      return 1;
    }
  if (pa1->aborted)
    {
      std::cerr << "--ABORT-- reading first automaton\n";
      return 1;
    }
  
  // Parse second automaton
  spot::parsed_aut_ptr pa2 = parse_aut(filename2, dict);
  if (pa2->format_errors(std::cerr))
    {
      std::cerr << "Error parsing second automaton: " << filename2 << '\n';
      return 1;
    }
  if (pa2->aborted)
    {
      std::cerr << "--ABORT-- reading second automaton\n";
      return 1;
    }
  
  // Prepare both automata (convert to state-based acceptance and split edges)
  spot::twa_graph_ptr aut1 = prepare_automaton(pa1->aut);
  spot::twa_graph_ptr aut2 = prepare_automaton(pa2->aut);
  
  // Collect conditions from both automata
  std::map<std::string, bdd> conds1 = collect_conditions(aut1);
  std::map<std::string, bdd> conds2 = collect_conditions(aut2);
  
  // Create unified condition mapping
  std::map<std::string, unsigned> cond_str_to_int = create_condition_mapping(conds1, conds2);
  
  // Merge condition maps for printing and mapping output
  std::map<std::string, bdd> all_conds = conds1;
  all_conds.insert(conds2.begin(), conds2.end());
  
  // Generate output filenames. If the input filename has a trailing
  // ".hoa" extension (after the last path separator), remove it and
  // replace with ".ba". Otherwise append ".ba" to the given name.
  auto make_output_name = [](const char* fname) -> std::string {
    std::string s(fname);
    // find last directory separator to avoid stripping dots in the path
    size_t pos_dir = s.find_last_of("/\\");
    size_t pos_dot = s.find_last_of('.');
    if (pos_dot != std::string::npos && pos_dot > pos_dir) {
      std::string ext = s.substr(pos_dot);
      if (ext == ".hoa") {
        return s.substr(0, pos_dot) + ".ba";
      }
    }
    return s + ".ba";
  };

  std::string output1 = make_output_name(filename1);
  std::string output2 = make_output_name(filename2);
  
  // Extract base filenames for the mapping file to avoid directory issues
  std::string base1(filename1);
  std::string base2(filename2);
  size_t pos1 = base1.find_last_of("/\\");
  if (pos1 != std::string::npos)
    base1 = base1.substr(pos1 + 1);
  size_t pos2 = base2.find_last_of("/\\");
  if (pos2 != std::string::npos)
    base2 = base2.substr(pos2 + 1);
  std::string mapping_filename = base1 + "_" + base2 + ".mapping";
  
  // Write first automaton to BA format
  std::ofstream out1(output1);
  if (!out1)
    {
      std::cerr << "Error opening output file: " << output1 << '\n';
      return 1;
    }
  print_ba_format(out1, aut1, cond_str_to_int);
  out1.close();
  std::cout << "Written first automaton to: " << output1 << '\n';
  
  // Write second automaton to BA format
  std::ofstream out2(output2);
  if (!out2)
    {
      std::cerr << "Error opening output file: " << output2 << '\n';
      return 1;
    }
  print_ba_format(out2, aut2, cond_str_to_int);
  out2.close();
  std::cout << "Written second automaton to: " << output2 << '\n';
  
  return 0;
}