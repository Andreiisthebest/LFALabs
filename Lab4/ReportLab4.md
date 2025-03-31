# Regular expressions
### Course: Formal Languages & Finite Automata
### Author: Bobeica Andrei
### Variant: 2

----

## Theory

### What are regular expressions?

Regular expressions (regex or regexp) are specialized text patterns that describe search criteria. They act as a powerful query language for text, allowing you to specify complex patterns to match, extract, or manipulate strings. Developed in the 1950s by mathematician Stephen Cole Kleene as a notation for regular languages, they've become an indispensable tool in computing, text processing, and data analysis.
At their core, regex patterns define rules for matching character sequences, enabling precise text operations that would be cumbersome or impossible with simple string methods. Their compact syntax packs remarkable expressive power, making them both challenging to master and incredibly valuable once understood.

### What Are Regular Expressions Used For?

Regular expressions are essential tools for text processing across many domains. Developers use them for validating user input like email addresses or phone numbers. Data analysts employ regex for searching through large datasets to find specific patterns or extracting particular information from unstructured text.

They excel at tasks such as:
- **Validation** of formatted strings like postal codes or credit card numbers
- **Search and replace** operations in text editors and word processors
- **Data extraction** from logs, documents, or web pages

### Basic Regex Components

The pattern `^\d{3}-\d{2}-\d{4}$` would match a U.S. Social Security Number format (123-45-6789) by combining several fundamental building blocks:

Literal characters match exactly as written, while metacharacters like the period (.) match any single character. Quantifiers such as asterisk (*), plus (+), and curly braces ({n}) control how many times a pattern should match. Character classes defined with square brackets [abc] match any character from the specified set.

This syntax follows formal language theory principles, making patterns both precise and computationally efficient. Despite their cryptic appearance, they represent a formal grammar that can be processed by finite state machines. This theoretical foundation enables regex engines to perform complex pattern matching with remarkable efficiency.

These patterns are implemented in virtually all programming languages, text editors, and many command-line tools, making them a universal skill for anyone working with text data.

## Objectives

The primary objectives of this lab are to:

1. Write and cover what regular expressions are, what they are used for;
2. Write a code that will generate valid combinations of symbols conform given regular expressions by giving a set of regexes as input and get valid word as an output
3. Write a function that will show sequence of processing regular expression
## Implementation description

In this section, i will talk about the implementation of the Regular expression combinations generator and explain each part of the code separately.


### tokenize method

The ```tokenize``` method has the purpose of breaking down regex patterns into understandable patterns for the code:

```
    def tokenize(self, regex_str):
        self.steps.append(f"1. Tokenizing: '{regex_str}'")

        patterns = [
            (r'\([^()]+\)(?:\^?\d+|\*|\+|\?)?', 'group'),  # Groups with quantifiers
            (r'[A-Za-z0-9δ]\*', 'zero_or_more'),           # Zero or more
            (r'[A-Za-z0-9δ]\+', 'one_or_more'),            # One or more
            (r'[A-Za-z0-9δ]\^\+', 'one_or_more_pow'),      # One or more with ^
            (r'[A-Za-z0-9δ]\?', 'optional'),               # Optional
            (r'[A-Za-z0-9δ]\^\d+', 'repeat_pow'),          # Exact repetition with ^
            (r'[A-Za-z0-9δ]\d+', 'repeat'),                # Exact repetition
            (r'[A-Za-z0-9δ]', 'literal')                   # Literal characters
        ]

        tokens = []
        i = 0
        while i < len(regex_str):
            matched = False
            for pattern, token_type in patterns:
                match = re.match(pattern, regex_str[i:])
                if match:
                    token_text = match.group(0)
                    tokens.append((token_text, token_type))
                    i += len(token_text)
                    matched = True
                    break

            if not matched:
                if regex_str[i].isspace():
                    i += 1
                else:
                    tokens.append((regex_str[i], 'literal'))
                    i += 1

        token_summary = ", ".join([f"'{t[0]}' ({t[1]})" for t in tokens])
        self.steps.append(f"2. Tokens identified: {token_summary}")
        return tokens
```

The way it works is that it starts by logging the tokenization step, and then defines the pattern matches for different regex elements, those elements being:
* Groups with quantifiers ```(abc)*```
* Zero-or-more ```a*```
* One-or-more ```b*```
* Optionals ```c?```
* Literal repetitions 
* Simple literals

The method has multiple layers of processing. As previously mentioned, it begins by logging the input string. After that, it defines a priority-ordered list of pattern matches, with groups being highest priority and applies patterns sequentially until all tokens are identified.

### parse_group method

This method handles the regex structures through patterns analysis, and returns both the alternatives and repetition counts, providing everything necessary for the subsequent  random generation

```
        def parse_group(self, group_token):
       
        match = re.match(r'\(([^()]+)\)(?:(?:\^?([*+?]))|(?:\^?(\d+)))?', group_token)
        if not match:
            return [group_token], [1]

        content = match.group(1)
        operator = match.group(2)
        repeat_count = match.group(3)

        alternatives = [alt.strip() for alt in content.split('|')]

        if operator == '*':
            possible_counts = range(self.max_repetitions + 1)
            rep_type = "zero or more (0-5)"
        elif operator == '+':
            possible_counts = range(1, self.max_repetitions + 1)
            rep_type = "one or more (1-5)"
        elif operator == '?':
            possible_counts = range(2)
            rep_type = "optional (0-1)"
        elif repeat_count:
            count = int(repeat_count)
            possible_counts = [count]
            rep_type = f"exactly {count}"
        else:
            possible_counts = [1]
            rep_type = "exactly 1"

        self.steps.append(f"- Group '{group_token}': alternatives={alternatives}, repetition={rep_type}")
        return alternatives, possible_counts
```
The key aspects of this method are:
* Structural parsing through the usage of a regex in order to decompose groups into content and quantifiers
* It splits group content by ```|``` to identify all valid options
* Distinguishes between ```*```, ```+```, ```?``` and exact counts
* And handles bare groups without quantifiers



### The generate_combinations method

This is the core generation method which combines all the components. It has a multi-stage process, which starts by iterating through the tokens to build outputs, and then makes probabilistic choices for alternatives and repetitions. Each token type has its own custom handling:
* Literals are included as they are
* Quantifiers  generate appropriate character repetitions
* Groups trigger recursive  alternative selection
* Special cases such as exponents are getting normalized before being processed
```
    def generate_combinations(self, regex_str, count=10, seed=None):
        if seed is not None:
            random.seed(seed)

        self.steps = []
        self.steps.append(f"Processing regex: '{regex_str}'")

        tokens = self.tokenize(regex_str)
        combinations = []

        for i in range(count):
            combination = []
            self.steps.append(f"\nCombination #{i + 1}:")

            for token, token_type in tokens:
                if token_type == 'literal':
                    combination.append(token)
                    self.steps.append(f"- Literal '{token}': added")

                elif token_type == 'zero_or_more':
                    char = token[0]
                    rep_count = random.randint(0, self.max_repetitions)
                    combination.append(char * rep_count)
                    self.steps.append(f"- '{char}*': using {rep_count} occurrences")

                elif token_type == 'one_or_more':
                    char = token[0]
                    rep_count = random.randint(1, self.max_repetitions)
                    combination.append(char * rep_count)
                    self.steps.append(f"- '{char}+': using {rep_count} occurrences")

                elif token_type == 'one_or_more_pow':
                    char = token[0]
                    rep_count = random.randint(1, self.max_repetitions)
                    combination.append(char * rep_count)
                    self.steps.append(f"- '{char}^+': using {rep_count} occurrences")

                elif token_type == 'optional':
                    char = token[0]
                    rep_count = random.randint(0, 1)
                    if rep_count == 1:
                        combination.append(char)
                        self.steps.append(f"- '{char}?': included")
                    else:
                        self.steps.append(f"- '{char}?': omitted")

                elif token_type == 'repeat':
                    match = re.match(r'([A-Za-z0-9δ])(\d+)', token)
                    if match:
                        char, cnt = match.groups()
                        cnt = int(cnt)
                        combination.append(char * cnt)
                        self.steps.append(f"- '{char}{cnt}': repeated {cnt} times")
                    else:
                        self.steps.append(f"- Failed to parse repeat token: '{token}'")
                        combination.append(token)

                elif token_type == 'repeat_pow':
                    match = re.match(r'([A-Za-z0-9δ])\^(\d+)', token)
                    if match:
                        char, cnt = match.groups()
                        cnt = int(cnt)
                        combination.append(char * cnt)
                        self.steps.append(f"- '{char}^{cnt}': repeated {cnt} times")
                    else:
                        self.steps.append(f"- Failed to parse repeat_pow token: '{token}'")
                        combination.append(token)

                elif token_type == 'group':
                    alternatives, possible_counts = self.parse_group(token)
                    repeat_count = random.choice(possible_counts)

                    if repeat_count > 0:
                        chosen_alternative = random.choice(alternatives)
                        group_value = chosen_alternative * repeat_count
                        self.steps.append(
                            f"- Group '{token}': selected '{chosen_alternative}' repeated {repeat_count} times")
                    else:
                        group_value = ""
                        self.steps.append(f"- Group '{token}': selected 0 repetitions")

                    combination.append(group_value)

            result = ''.join(combination)
            combinations.append(result)
            self.steps.append(f"- Final combination: '{result}'")

        return combinations
```

Besides that, it has step logging and provides step by step display of every decision taken by the code so that the logic of the generation behaviour becomes clearer, by mentioning each taken decision ```Literal 'K' added``` , occurrences ```'J+': using 4 occurences``` and repetitions ```repetition= zero or more```
### The main function



```
def main():
    generator = RegexCombinationGenerator(max_repetitions=5)

    example_regexes = [
        "O(P|Q|R)+ 2(3|4)",
        "A*B(C|D|E)F(G|H|I)²",
        "J+K(L|M|N)*O?(P|Q)³"
    ]

    for regex in example_regexes:
        print(f"\nGenerating combinations for: {regex}")
        combinations = generator.generate_combinations(regex, count=5)
        print("Sample combinations:")
        for combo in combinations:
            print(f"  - {combo}")

        print("\nProcessing steps:")
        for step in generator.get_processing_steps():
            print(f"  {step}")
```
The purpose of the ```main``` function is simply to demonstrage the usage of the code. The way it works is that it:
* Creates a generator instance
* Processes  the sample regex patterns
* Displays both the results and the step-by-step proccesing logic.




## Results
```
Generating combinations for: M?N^2(O|P)^3Q*R^+
Sample combinations:
  - MNNPPPRRRRR
  - MNNPPPRRR
  - MNNPPPQRRRR
  - NNOOOQQQRRRR
  - NNOOOQQRRRR

Processing steps:
  Processing regex: 'M?N^2(O|P)^3Q*R^+'
  1. Tokenizing: 'M?N^2(O|P)^3Q*R^+'
  2. Tokens identified: 'M?' (optional), 'N^2' (repeat_pow), '(O|P)^3' (group), 'Q*' (zero_or_more), 'R^+' (one_or_more_pow)
  
Combination #1:
  - 'M?': included
  - 'N^2': repeated 2 times
  - Group '(O|P)^3': alternatives=['O', 'P'], repetition=exactly 3
  - Group '(O|P)^3': selected 'P' repeated 3 times
  - 'Q*': using 0 occurrences
  - 'R^+': using 5 occurrences
  - Final combination: 'MNNPPPRRRRR'
  
Combination #2:
  - 'M?': included
  - 'N^2': repeated 2 times
  - Group '(O|P)^3': alternatives=['O', 'P'], repetition=exactly 3
  - Group '(O|P)^3': selected 'P' repeated 3 times
  - 'Q*': using 0 occurrences
  - 'R^+': using 3 occurrences
  - Final combination: 'MNNPPPRRR'
  
Combination #3:
  - 'M?': included
  - 'N^2': repeated 2 times
  - Group '(O|P)^3': alternatives=['O', 'P'], repetition=exactly 3
  - Group '(O|P)^3': selected 'P' repeated 3 times
  - 'Q*': using 1 occurrences
  - 'R^+': using 4 occurrences
  - Final combination: 'MNNPPPQRRRR'
  
Combination #4:
  - 'M?': omitted
  - 'N^2': repeated 2 times
  - Group '(O|P)^3': alternatives=['O', 'P'], repetition=exactly 3
  - Group '(O|P)^3': selected 'O' repeated 3 times
  - 'Q*': using 3 occurrences
  - 'R^+': using 4 occurrences
  - Final combination: 'NNOOOQQQRRRR'
  
Combination #5:
  - 'M?': omitted
  - 'N^2': repeated 2 times
  - Group '(O|P)^3': alternatives=['O', 'P'], repetition=exactly 3
  - Group '(O|P)^3': selected 'O' repeated 3 times
  - 'Q*': using 2 occurrences
  - 'R^+': using 4 occurrences
  - Final combination: 'NNOOOQQRRRR'

Generating combinations for: (X|Y|Z)^38^+(9|o)^2
Sample combinations:
  - YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY^+99
  - ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ^+99
  - YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY^+99
  - XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX^+oo
  - ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ^+oo

Processing steps:
  Processing regex: '(X|Y|Z)^38^+(9|o)^2'
  1. Tokenizing: '(X|Y|Z)^38^+(9|o)^2'
  2. Tokens identified: '(X|Y|Z)^38' (group), '^' (literal), '+' (literal), '(9|o)^2' (group)
  
Combination #1:
  - Group '(X|Y|Z)^38': alternatives=['X', 'Y', 'Z'], repetition=exactly 38
  - Group '(X|Y|Z)^38': selected 'Y' repeated 38 times
  - Literal '^': added
  - Literal '+': added
  - Group '(9|o)^2': alternatives=['9', 'o'], repetition=exactly 2
  - Group '(9|o)^2': selected '9' repeated 2 times
  - Final combination: 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY^+99'
  
Combination #2:
  - Group '(X|Y|Z)^38': alternatives=['X', 'Y', 'Z'], repetition=exactly 38
  - Group '(X|Y|Z)^38': selected 'Z' repeated 38 times
  - Literal '^': added
  - Literal '+': added
  - Group '(9|o)^2': alternatives=['9', 'o'], repetition=exactly 2
  - Group '(9|o)^2': selected '9' repeated 2 times
  - Final combination: 'ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ^+99'
  
Combination #3:
  - Group '(X|Y|Z)^38': alternatives=['X', 'Y', 'Z'], repetition=exactly 38
  - Group '(X|Y|Z)^38': selected 'Y' repeated 38 times
  - Literal '^': added
  - Literal '+': added
  - Group '(9|o)^2': alternatives=['9', 'o'], repetition=exactly 2
  - Group '(9|o)^2': selected '9' repeated 2 times
  - Final combination: 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY^+99'
  
Combination #4:
  - Group '(X|Y|Z)^38': alternatives=['X', 'Y', 'Z'], repetition=exactly 38
  - Group '(X|Y|Z)^38': selected 'X' repeated 38 times
  - Literal '^': added
  - Literal '+': added
  - Group '(9|o)^2': alternatives=['9', 'o'], repetition=exactly 2
  - Group '(9|o)^2': selected 'o' repeated 2 times
  - Final combination: 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX^+oo'
  
Combination #5:
  - Group '(X|Y|Z)^38': alternatives=['X', 'Y', 'Z'], repetition=exactly 38
  - Group '(X|Y|Z)^38': selected 'Z' repeated 38 times
  - Literal '^': added
  - Literal '+': added
  - Group '(9|o)^2': alternatives=['9', 'o'], repetition=exactly 2
  - Group '(9|o)^2': selected 'o' repeated 2 times
  - Final combination: 'ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ^+oo'

Generating combinations for: (H|i)(J|K)L*N?
Sample combinations:
  - HKL
  - iKLLLL
  - iKLLLLLN
  - HJLLL
  - iKL

Processing steps:
  Processing regex: '(H|i)(J|K)L*N?'
  1. Tokenizing: '(H|i)(J|K)L*N?'
  2. Tokens identified: '(H|i)' (group), '(J|K)' (group), 'L*' (zero_or_more), 'N?' (optional)
  
Combination #1:
  - Group '(H|i)': alternatives=['H', 'i'], repetition=exactly 1
  - Group '(H|i)': selected 'H' repeated 1 times
  - Group '(J|K)': alternatives=['J', 'K'], repetition=exactly 1
  - Group '(J|K)': selected 'K' repeated 1 times
  - 'L*': using 1 occurrences
  - 'N?': omitted
  - Final combination: 'HKL'
  
Combination #2:
  - Group '(H|i)': alternatives=['H', 'i'], repetition=exactly 1
  - Group '(H|i)': selected 'i' repeated 1 times
  - Group '(J|K)': alternatives=['J', 'K'], repetition=exactly 1
  - Group '(J|K)': selected 'K' repeated 1 times
  - 'L*': using 4 occurrences
  - 'N?': omitted
  - Final combination: 'iKLLLL'
  
Combination #3:
  - Group '(H|i)': alternatives=['H', 'i'], repetition=exactly 1
  - Group '(H|i)': selected 'i' repeated 1 times
  - Group '(J|K)': alternatives=['J', 'K'], repetition=exactly 1
  - Group '(J|K)': selected 'K' repeated 1 times
  - 'L*': using 5 occurrences
  - 'N?': included
  - Final combination: 'iKLLLLLN'
  
Combination #4:
  - Group '(H|i)': alternatives=['H', 'i'], repetition=exactly 1
  - Group '(H|i)': selected 'H' repeated 1 times
  - Group '(J|K)': alternatives=['J', 'K'], repetition=exactly 1
  - Group '(J|K)': selected 'J' repeated 1 times
  - 'L*': using 3 occurrences
  - 'N?': omitted
  - Final combination: 'HJLLL'
  
Combination #5:
  - Group '(H|i)': alternatives=['H', 'i'], repetition=exactly 1
  - Group '(H|i)': selected 'i' repeated 1 times
  - Group '(J|K)': alternatives=['J', 'K'], repetition=exactly 1
  - Group '(J|K)': selected 'K' repeated 1 times
  - 'L*': using 1 occurrences
  - 'N?': omitted
  - Final combination: 'iKL'
```

## Conclusion

In this lab, we explored the fundamentals of regular expressions, their practical applications, and their connection to formal language theory. We developed a regex-based word generator that can parse, tokenize, and process regex patterns to generate valid string combinations. The implementation effectively decomposes regex patterns into recognizable components, handles quantifiers and groups, and constructs randomized yet conforming outputs.

Through systematic tokenization, parsing, and generation steps, we demonstrated how regex can be programmatically interpreted to produce structured outputs. The logging mechanism provides a clear view of how each pattern is processed, making the approach both transparent and debuggable.

Overall, this project illustrates the computational power of regular expressions and their role in automating text processing tasks. The developed solution not only reinforces the theoretical understanding of finite automata and formal languages but also has practical applications in fields like data validation, lexical analysis, and pattern recognition.


## References

[1] [A sample of a regular expression implementation](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html)

[2] [Regular expressions](https://en.wikipedia.org/wiki/Lexical_analysis)

[3] [Formal Languages and Finite Automata, Guide for practical lessons](https://else.fcim.utm.md/pluginfile.php/110458/mod_resource/content/0/LFPC_Guide.pdf)