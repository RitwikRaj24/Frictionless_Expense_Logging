import 'package:flutter/material.dart';
import 'dart:math';

void main() {
  runApp(const MyApp());
}

// --- 1. CONFIGURATION (DARK MODE) ---
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Frictionless Expenses',
      theme: ThemeData(
        brightness: Brightness.dark, 
        primaryColor: const Color(0xFF2E3A59),
        scaffoldBackgroundColor: const Color(0xFF121212), 
        useMaterial3: true,
        // FIX: Changed CardTheme to CardThemeData for your version of Flutter
        cardTheme: CardThemeData(
          color: const Color(0xFF1E1E1E), 
          elevation: 4,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
        ),
      ),
      home: const MainShell(),
    );
  }
}

// --- 2. MAIN SHELL ---
class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _selectedIndex = 0;
  final double _monthlyBudget = 5000; 

  // DATA
  final List<Map<String, dynamic>> _transactions = [
    {"category": "Food", "amount": 150, "time": "10:30 AM"},
    {"category": "Stationary", "amount": 40, "time": "Yesterday"},
    {"category": "Dorm", "amount": 500, "time": "Yesterday"},
    {"category": "Travel", "amount": 50, "time": "2 days ago"},
  ];

  void _addTransaction(String category, int amount) {
    setState(() {
      _transactions.insert(0, {
        "category": category,
        "amount": amount,
        "time": "Just now"
      });
    });
  }

  void _deleteTransaction(int index) {
    // 1. Store item for Undo
    final deletedItem = _transactions[index];
    
    setState(() {
      _transactions.removeAt(index);
    });

    // 2. Show Undo Snackbar
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text("Deleted ${deletedItem['category']}"),
        action: SnackBarAction(
          label: "UNDO",
          onPressed: () {
            setState(() {
              _transactions.insert(index, deletedItem);
            });
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> pages = [
      HomeTab(
        transactions: _transactions,
        onAdd: _addTransaction,
        onDelete: _deleteTransaction,
      ),
      StatsTab(
        transactions: _transactions,
        budget: _monthlyBudget,
      ),
    ];

    return Scaffold(
      body: pages[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (int index) => setState(() => _selectedIndex = index),
        backgroundColor: const Color(0xFF1E1E1E), 
        indicatorColor: const Color(0xFF2E3A59),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined, color: Colors.white70),
            selectedIcon: Icon(Icons.home, color: Colors.white),
            label: 'Log',
          ),
          NavigationDestination(
            icon: Icon(Icons.pie_chart_outline, color: Colors.white70),
            selectedIcon: Icon(Icons.pie_chart, color: Colors.white),
            label: 'Stats',
          ),
        ],
      ),
    );
  }
}

// --- 3. HOME TAB (DARK) ---
class HomeTab extends StatefulWidget {
  final List<Map<String, dynamic>> transactions;
  final Function(String, int) onAdd;
  final Function(int) onDelete;

  const HomeTab({
    super.key,
    required this.transactions,
    required this.onAdd,
    required this.onDelete,
  });

  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  String _amount = "";

  void _addQuickAmount(int value) {
    setState(() {
      int current = int.tryParse(_amount) ?? 0;
      _amount = (current + value).toString();
    });
  }

  void _handlePayment(String category) async {
    if (_amount.isEmpty || _amount == "0") return;
    print("Launching UPI for $category: ₹$_amount");
    await Future.delayed(const Duration(milliseconds: 500));
    if (!mounted) return;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E1E1E),
        title: const Text("Confirm Payment", style: TextStyle(color: Colors.white)),
        content: const Text("Did the transaction succeed?", style: TextStyle(color: Colors.white70)),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(), child: const Text("No")),
          TextButton(
            onPressed: () {
              widget.onAdd(category, int.parse(_amount));
              setState(() => _amount = "");
              Navigator.of(ctx).pop();
            },
            child: const Text("Yes", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Header
        Container(
          width: double.infinity,
          padding: const EdgeInsets.only(left: 20, right: 20, top: 60, bottom: 30),
          decoration: const BoxDecoration(
            color: Color(0xFF1E1E1E), 
            borderRadius: BorderRadius.only(bottomLeft: Radius.circular(30), bottomRight: Radius.circular(30)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Text("Good Evening,", style: TextStyle(color: Colors.white54, fontSize: 14)),
              SizedBox(height: 5),
              Text("Student", style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
            ],
          ),
        ),
        Expanded(
          child: SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 20),
                // Input Card
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 20),
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E1E1E), 
                    borderRadius: BorderRadius.circular(15),
                    boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.5), blurRadius: 10, offset: const Offset(0, 5))],
                  ),
                  child: Column(
                    children: [
                      const Text("How much?", style: TextStyle(color: Colors.white54)),
                      TextField(
                        controller: TextEditingController(text: _amount),
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white),
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(prefixText: "₹ ", border: InputBorder.none, prefixStyle: TextStyle(color: Colors.white)),
                        onChanged: (val) => _amount = val,
                      ),
                      const SizedBox(height: 10),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          _buildQuickChip(10), const SizedBox(width: 10),
                          _buildQuickChip(20), const SizedBox(width: 10),
                          _buildQuickChip(50),
                        ],
                      )
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                // Categories
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _buildCategoryBtn("Food", Icons.fastfood, Colors.blue),
                    const SizedBox(width: 15),
                    _buildCategoryBtn("Stationary", Icons.edit, Colors.orange),
                    const SizedBox(width: 15),
                    _buildCategoryBtn("Dorm", Icons.bed, Colors.purple),
                  ],
                ),
                const SizedBox(height: 30),
                // List
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(horizontal: 25),
                  child: const Text("Recent Transactions", style: TextStyle(color: Colors.white70, fontSize: 18, fontWeight: FontWeight.bold)),
                ),
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: widget.transactions.length,
                  itemBuilder: (context, index) {
                    final item = widget.transactions[index];
                    return Column(
                      children: [
                        ListTile(
                          leading: const Icon(Icons.receipt_long, color: Colors.blueAccent),
                          title: Text(item['category'], style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                          subtitle: Text(item['time'], style: const TextStyle(color: Colors.white38)),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text("- ₹${item['amount']}", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.white)),
                              IconButton(
                                icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
                                onPressed: () => widget.onDelete(index),
                              ),
                            ],
                          ),
                        ),
                        const Divider(height: 1, indent: 20, endIndent: 20, color: Colors.white12),
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildQuickChip(int value) {
    return InkWell(
      onTap: () => _addQuickAmount(value),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 8),
        decoration: BoxDecoration(color: const Color(0xFF2C2C2C), borderRadius: BorderRadius.circular(20)), 
        child: Text("+₹$value", style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold)),
      ),
    );
  }

  Widget _buildCategoryBtn(String label, IconData icon, Color color) {
    return InkWell(
      onTap: () => _handlePayment(label),
      child: Container(
        width: 100, height: 100,
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E1E), borderRadius: BorderRadius.circular(15),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.5), blurRadius: 5, offset: const Offset(0, 2))],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 30),
            const SizedBox(height: 5),
            Text(label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}

// --- 4. STATS TAB (With Pacing Score) ---
class StatsTab extends StatelessWidget {
  final List<Map<String, dynamic>> transactions;
  final double budget;

  const StatsTab({super.key, required this.transactions, required this.budget});

  Color _getColor(String category) {
    switch (category) {
      case "Food": return Colors.blue;
      case "Stationary": return Colors.orange;
      case "Dorm": return Colors.purple;
      case "Travel": return Colors.teal;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    // 1. Calculations
    double totalSpent = 0;
    Map<String, double> categoryTotals = {};
    for (var item in transactions) {
      double amt = (item['amount'] as int).toDouble();
      totalSpent += amt;
      categoryTotals[item['category']] = (categoryTotals[item['category']] ?? 0) + amt;
    }

    // 2. Pacing Logic
    DateTime now = DateTime.now();
    int dayOfMonth = now.day;
    int daysInMonth = 30; 
    
    double idealPerDay = budget / daysInMonth;
    double actualPerDay = dayOfMonth > 0 ? totalSpent / dayOfMonth : 0;
    double pacingScore = idealPerDay > 0 ? actualPerDay / idealPerDay : 0;
    
    String pacingText;
    Color pacingColor;
    if (pacingScore < 0.8) {
      pacingText = "Safe Saver";
      pacingColor = Colors.greenAccent;
    } else if (pacingScore <= 1.2) {
      pacingText = "On Track";
      pacingColor = Colors.blueAccent;
    } else {
      pacingText = "Overspending!";
      pacingColor = Colors.redAccent;
    }

    return Column(
      children: [
        // Header with Pacing
        Container(
          width: double.infinity,
          padding: const EdgeInsets.only(left: 20, right: 20, top: 60, bottom: 30),
          decoration: const BoxDecoration(
            color: Color(0xFF1E1E1E),
            borderRadius: BorderRadius.only(bottomLeft: Radius.circular(30), bottomRight: Radius.circular(30)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text("Total Spent", style: TextStyle(color: Colors.white54, fontSize: 14)),
                      const SizedBox(height: 5),
                      Text("₹${totalSpent.toStringAsFixed(0)}", style: const TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  // PACING SCORE CARD
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: pacingColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: pacingColor.withOpacity(0.5))
                    ),
                    child: Column(
                      children: [
                        Text("${pacingScore.toStringAsFixed(1)}x", style: TextStyle(color: pacingColor, fontWeight: FontWeight.bold, fontSize: 20)),
                        Text(pacingText, style: TextStyle(color: pacingColor, fontSize: 10)),
                      ],
                    ),
                  )
                ],
              ),
              const SizedBox(height: 20),
              // Linear Pacing Bar
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: LinearProgressIndicator(
                  value: (totalSpent / budget).clamp(0.0, 1.0),
                  minHeight: 8,
                  backgroundColor: Colors.white10,
                  valueColor: AlwaysStoppedAnimation<Color>(pacingColor),
                ),
              ),
              const SizedBox(height: 5),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text("0%", style: TextStyle(color: Colors.white24, fontSize: 10)),
                  Text("Limit: ₹${budget.toStringAsFixed(0)}", style: const TextStyle(color: Colors.white24, fontSize: 10)),
                ],
              )
            ],
          ),
        ),

        Expanded(
          child: SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 30),
                const Text("Category Breakdown", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                const SizedBox(height: 20),
                
                // Chart
                SizedBox(
                  height: 200, width: 200,
                  child: CustomPaint(
                    painter: PieChartPainter(
                      data: categoryTotals,
                      total: totalSpent,
                      colorMapper: _getColor,
                    ),
                    child: Center(child: Text("₹${totalSpent.toStringAsFixed(0)}", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: Colors.white))),
                  ),
                ),
                
                const SizedBox(height: 30),

                // Legend
                ListView(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  children: categoryTotals.entries.map((entry) {
                    return Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 15),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E1E1E), borderRadius: BorderRadius.circular(10),
                        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 2)],
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(children: [
                            Icon(Icons.circle, color: _getColor(entry.key), size: 14),
                            const SizedBox(width: 10),
                            Text(entry.key, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                          ]),
                          Text("₹${entry.value.toStringAsFixed(0)}", style: const TextStyle(color: Colors.white70)),
                        ],
                      ),
                    );
                  }).toList(),
                ),
                const SizedBox(height: 50),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// --- 5. NATIVE PIE CHART ENGINE (Dark Mode) ---
class PieChartPainter extends CustomPainter {
  final Map<String, double> data;
  final double total;
  final Color Function(String) colorMapper;

  PieChartPainter({required this.data, required this.total, required this.colorMapper});

  @override
  void paint(Canvas canvas, Size size) {
    double startAngle = -pi / 2; 
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;
    final strokeWidth = 25.0;

    // Background Circle
    final bgPaint = Paint()
      ..color = Colors.white10 
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth;
    canvas.drawCircle(center, radius, bgPaint);

    if (total == 0) return;

    data.forEach((category, value) {
      final sweepAngle = (value / total) * 2 * pi;
      final paint = Paint()
        ..color = colorMapper(category)
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.butt;

      canvas.drawArc(Rect.fromCircle(center: center, radius: radius), startAngle, sweepAngle, false, paint);
      startAngle += sweepAngle;
    });
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}