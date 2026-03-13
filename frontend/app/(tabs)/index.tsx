import Ionicons from '@expo/vector-icons/Ionicons';
import DateTimePicker from '@react-native-community/datetimepicker';
import { useRouter } from 'expo-router';
import React, { useRef, useState } from "react";
import {
  Dimensions,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import apiClient from '../../lib/services/apiClient';
import { Category, Transaction, TransactionType } from '../../lib/types/transaction.types';

// ─── Constants ────────────────────────────────────────────────────────────────

const CURRENCIES = ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CNY', 'AUD', 'CAD', 'KRW', 'SGD'];
const PAGE_SIZE = 6;
const MAX_RECENT = 10;
const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

const UPPER_HALF_HEIGHT = SCREEN_HEIGHT * 0.4 - 44 - 28 - 12;
const TILE_GAP = 6;
const TILE_FROM_WIDTH = (SCREEN_WIDTH - 24 - TILE_GAP * 2) / 3;
const TILE_FROM_HEIGHT = (UPPER_HALF_HEIGHT - TILE_GAP) / 2;
const TILE_SIZE = Math.floor(Math.min(TILE_FROM_WIDTH, TILE_FROM_HEIGHT));

// ─── Mock Data ────────────────────────────────────────────────────────────────

const INITIAL_CATEGORIES: Category[] = [
  { id: 1, title: 'Transport', amount: 0 },
  { id: 2, title: 'Food', amount: 0 },
  { id: 3, title: 'Shopping', amount: 0 },
  { id: 4, title: 'Housing', amount: 0 },
  { id: 5, title: 'Health', amount: 0 },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────

const formatDate = (date: Date): string =>
  date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });

const formatDayHeading = (dateStr: string): string => {
  const d = new Date(dateStr);
  const day = d.getDate();
  const suffix = ['th', 'st', 'nd', 'rd'][
    day % 10 <= 3 && ![11, 12, 13].includes(day % 100) ? day % 10 : 0
  ];
  return `${day}${suffix} ${d.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })}`;
};

const formatMonthHeading = (dateStr: string): string => {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' }).toUpperCase();
};

// ─── Category Tile ────────────────────────────────────────────────────────────

const CategoryTile = ({
  id, title, amount, exposeMenu, onPress, handleDeleteCategory,
}: {
  id: number; title: string; amount: number; exposeMenu: boolean;
  onPress: () => void; handleDeleteCategory: (id: number) => void;
}) => (
  <Pressable
    style={styles.tile}
    onPress={() => { if (!exposeMenu) onPress(); }}
  >
    {exposeMenu && (
      <Pressable style={styles.removeButton} onPress={() => handleDeleteCategory(id)}>
        <Ionicons name="remove-circle" size={22} color="#a90000c1" />
      </Pressable>
    )}
    <Text style={styles.tileTitle} numberOfLines={2}>{title}</Text>
    <Text style={styles.tileAmount}>{amount.toFixed(2)}</Text>
  </Pressable>
);

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function Index() {
  const router = useRouter();

  const [categories, setCategories] = useState<Category[]>(INITIAL_CATEGORIES);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  // NOTE: When GET /transactions is ready, replace the empty array above with
  // a useEffect that calls apiClient.getTransactions() and sets state on mount.

  const [exposeMenu, setExposeMenu] = useState(false);

  const [categoryPage, setCategoryPage] = useState(0);
  const categoryScrollRef = useRef<ScrollView>(null);

  const [modalCatVisible, setModalCat] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");

  const [modalTraVisible, setModalTra] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [newAmount, setNewAmount] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [selectedCurrency, setSelectedCurrency] = useState("JPY");
  const [currencyDropdownVisible, setCurrencyDropdownVisible] = useState(false);

  const [selectedTransactionType, setSelectedTransactionType] = useState<TransactionType>('expense');

  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [datePickerVisible, setDatePickerVisible] = useState(false);

  // ── Derived ────────────────────────────────────────────────────────────────

  const totalSpending = transactions
    .filter(t => t.transaction_type === 'expense' || t.transaction_type === 'subscription')
    .reduce((sum, t) => sum + t.amount, 0);

  const totalIncome = transactions
    .filter(t => t.transaction_type === 'income')
    .reduce((sum, t) => sum + t.amount, 0);

  const categoryTransactions = transactions
    .filter(t => t.category === selectedCategory?.title)
    .sort((a, b) => new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime());

  const sortedTransactions = [...transactions].sort(
    (a, b) => new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime()
  );
  const recentTransactions = sortedTransactions.slice(0, MAX_RECENT);
  const hasMore = sortedTransactions.length > MAX_RECENT;

  const totalPages = Math.max(1, Math.ceil(categories.length / PAGE_SIZE));

  // ── Handlers ───────────────────────────────────────────────────────────────

  const handleOpenCategory = (category: Category) => {
    setSelectedCategory(category);
    setNewAmount("");
    setNewDescription("");
    setSelectedCurrency("JPY");
    setSelectedTransactionType('expense');
    setSelectedDate(new Date());
    setCurrencyDropdownVisible(false);
    setDatePickerVisible(false);
    setModalTra(true);
  };

  const handleCloseTransactionModal = () => {
    setModalTra(false);
    setCurrencyDropdownVisible(false);
    setDatePickerVisible(false);
  };

  const handleCreateCategory = () => {
    if (!newCategoryName.trim()) return;
    setCategories(prev => [...prev, {
      id: prev.length > 0 ? prev[prev.length - 1].id + 1 : 1,
      title: newCategoryName,
      amount: 0,
    }]);
    setNewCategoryName("");
    setModalCat(false);
  };

  const handleDeleteCategory = (id: number) => {
    setCategories(prev => prev.filter(c => c.id !== id));
  };

  const handleAddTransaction = async () => {
    const parsedAmount = parseFloat(newAmount);
    if (!newAmount.trim() || isNaN(parsedAmount) || parsedAmount <= 0) return;
    if (!selectedCategory) return;
    if (isSubmitting) return;

    // Build the local transaction for optimistic UI.
    // Uses a temporary negative id to distinguish from real API ids.
    const tempId = -Date.now();
    const optimisticTransaction: Transaction = {
      id: tempId,
      currency: selectedCurrency,
      amount: parsedAmount,
      transaction_type: selectedTransactionType,
      category: selectedCategory.title,
      description: newDescription || null,
      business_name: null,
      payment_method: null,
      exchange_rate: null,
      occurred_at: selectedDate.toISOString(),
    };

    // ── OPTIMISTIC UPDATE ──────────────────────────────────────────────────
    // Adds to local state immediately so the UI feels instant.
    // TO SWITCH TO SUCCESS-ONLY: remove these two setX calls and move them
    // into the try block below, replacing tempId with apiTransaction.id.
    setTransactions(prev => [...prev, optimisticTransaction]);
    setCategories(prev => prev.map(c =>
      c.id === selectedCategory.id ? { ...c, amount: c.amount + parsedAmount } : c
    ));
    // ── END OPTIMISTIC UPDATE ──────────────────────────────────────────────

    setNewAmount("");
    setNewDescription("");
    setSelectedDate(new Date());
    setIsSubmitting(true);

    try {
      await apiClient.postTransaction({
        amount: parsedAmount,
        exchange_rate: null,
        currency: selectedCurrency,
        transaction_type: selectedTransactionType,
        category: selectedCategory.title,
        description: newDescription || null,
        business_name: null,
        payment_method: null,
      });

      // TO SWITCH TO SUCCESS-ONLY: move setTransactions and setCategories here,
      // using the real id from the API response instead of tempId.

    } catch (error) {
      console.error('Failed to post transaction:', error);

      // Revert optimistic update on failure
      setTransactions(prev => prev.filter(t => t.id !== tempId));
      setCategories(prev => prev.map(c =>
        c.id === selectedCategory.id ? { ...c, amount: c.amount - parsedAmount } : c
      ));
    } finally {
      setIsSubmitting(false);
    }
  };

  // ── Transaction feed renderer ───────────────────────────────────────────────

  const renderTransactionFeed = () => {
    const items: React.ReactElement[] = [];
    let lastMonth = '';
    let lastDay = '';

    recentTransactions.forEach((t, i) => {
      const month = formatMonthHeading(t.occurred_at);
      const day = formatDayHeading(t.occurred_at);

      if (month !== lastMonth) {
        items.push(<Text key={`month-${i}`} style={styles.monthDivider}>{month}</Text>);
        lastMonth = month;
        lastDay = '';
      }

      if (day !== lastDay) {
        items.push(<Text key={`day-${i}`} style={styles.dayDivider}>{day}</Text>);
        lastDay = day;
      }

      items.push(
        <View key={t.id} style={styles.transactionRow}>
          <View style={[
            styles.categoryDot,
            t.transaction_type === 'income' && { backgroundColor: '#22c55e' },
            t.transaction_type === 'subscription' && { backgroundColor: '#6495ed' },
          ]} />
          <View style={{ flex: 1 }}>
            <Text style={styles.transactionDesc} numberOfLines={1}>
              {t.description || '—'}
            </Text>
            <Text style={styles.transactionCat}>{t.category}</Text>
          </View>
          <Text style={[
            styles.transactionAmount,
            t.transaction_type === 'income' && { color: '#22c55e' },
            t.transaction_type === 'subscription' && { color: '#6495ed' },
          ]}>
            {t.currency} {t.amount.toFixed(2)}
          </Text>
        </View>
      );
    });

    if (hasMore) {
      items.push(
        <Pressable
          key="see-all"
          style={styles.seeAllButton}
          onPress={() => router.push('/(tabs)/statistics')}
        >
          <Text style={styles.seeAllButtonText}>See all expenses</Text>
          <Ionicons name="arrow-forward" size={16} color="#6495ed" />
        </Pressable>
      );
    }

    return items;
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <Pressable style={styles.container} onLongPress={() => setExposeMenu(prev => !prev)}>

      {/* ── Upper half ── */}
      <View style={styles.upperHalf}>

        {/* Summary bar */}
        <View style={styles.summaryBar}>
          <View style={styles.summaryItem}>
            <Ionicons name="caret-up" size={14} color="#22c55e" />
            <Text style={styles.summaryIncome}>{totalIncome.toFixed(2)}</Text>
          </View>
          <View style={styles.summaryItem}>
            <Ionicons name="caret-down" size={14} color="#ef4444" />
            <Text style={styles.summarySpending}>{totalSpending.toFixed(2)}</Text>
          </View>
        </View>

        {/* Paginated category grid */}
        <ScrollView
          ref={categoryScrollRef}
          horizontal
          pagingEnabled
          showsHorizontalScrollIndicator={false}
          scrollEnabled={totalPages > 1}
          onMomentumScrollEnd={e => {
            const page = Math.round(e.nativeEvent.contentOffset.x / SCREEN_WIDTH);
            setCategoryPage(page);
          }}
          style={{ flex: 1 }}
        >
          {Array.from({ length: totalPages }).map((_, pageIndex) => {
            const pageCats = categories.slice(pageIndex * PAGE_SIZE, (pageIndex + 1) * PAGE_SIZE);
            const padded = [
              ...pageCats,
              ...Array(Math.max(0, PAGE_SIZE - pageCats.length)).fill(null),
            ];
            return (
              <View key={pageIndex} style={[styles.categoryPage, { width: SCREEN_WIDTH }]}>
                {padded.map((cat, idx) =>
                  cat ? (
                    <CategoryTile
                      key={cat.id}
                      id={cat.id}
                      title={cat.title}
                      amount={cat.amount}
                      exposeMenu={exposeMenu}
                      handleDeleteCategory={handleDeleteCategory}
                      onPress={() => handleOpenCategory(cat)}
                    />
                  ) : (
                    <View key={`empty-${idx}`} style={styles.tilePlaceholder} />
                  )
                )}
              </View>
            );
          })}
        </ScrollView>

        {/* Page indicator dots */}
        <View style={styles.dotsRow}>
          {totalPages > 1 && Array.from({ length: totalPages }).map((_, i) => (
            <Pressable
              key={i}
              onPress={() => {
                setCategoryPage(i);
                categoryScrollRef.current?.scrollTo({ x: i * SCREEN_WIDTH, animated: true });
              }}
            >
              <View style={[styles.dot, i === categoryPage && styles.dotActive]} />
            </Pressable>
          ))}
        </View>
      </View>

      {/* ── Lower half — recent expenses ── */}
      <ScrollView style={styles.lowerHalf} contentContainerStyle={{ paddingBottom: 100 }}>
        <Text style={styles.recentHeading}>Recent Expenses</Text>
        {sortedTransactions.length === 0
          ? <Text style={styles.noExpensesText}>No expenses yet</Text>
          : renderTransactionFeed()
        }
      </ScrollView>

      {/* ── Transaction Modal ── */}
      <Modal
        visible={modalTraVisible}
        transparent={true}
        animationType='slide'
        onRequestClose={handleCloseTransactionModal}
      >
        <View style={styles.modalTraOverlay}>
          <Pressable
            style={styles.modalTraContent}
            onPress={() => {
              setCurrencyDropdownVisible(false);
              setDatePickerVisible(false);
            }}
          >
            <View style={styles.modalTraHeader}>
              <Text style={styles.modalTraTitle}>{selectedCategory?.title}</Text>
              <Pressable onPress={handleCloseTransactionModal} style={styles.closeButton}>
                <Ionicons name="close" size={26} color="#555" />
              </Pressable>
            </View>

            {/* Amount + Currency row */}
            <View style={styles.inputRow}>
              <TextInput
                style={[styles.traInput, { flex: 1 }]}
                placeholder="0.00"
                placeholderTextColor="#aaa"
                value={newAmount}
                onChangeText={text => setNewAmount(text.replace(/[^0-9.]/g, ''))}
                keyboardType="decimal-pad"
                onFocus={() => {
                  setCurrencyDropdownVisible(false);
                  setDatePickerVisible(false);
                }}
              />
              <Pressable
                style={styles.currencyButton}
                onPress={() => {
                  setCurrencyDropdownVisible(prev => !prev);
                  setDatePickerVisible(false);
                }}
              >
                <Text style={styles.currencyButtonText}>{selectedCurrency}</Text>
                <Ionicons name="chevron-down" size={14} color="#fff" />
              </Pressable>
            </View>

            {currencyDropdownVisible && (
              <View style={styles.dropdown}>
                <ScrollView nestedScrollEnabled style={{ maxHeight: 200 }}>
                  {CURRENCIES.map(currency => (
                    <Pressable
                      key={currency}
                      style={[styles.dropdownItem, currency === selectedCurrency && styles.dropdownItemSelected]}
                      onPress={() => { setSelectedCurrency(currency); setCurrencyDropdownVisible(false); }}
                    >
                      <Text style={[styles.dropdownItemText, currency === selectedCurrency && styles.dropdownItemTextSelected]}>
                        {currency}
                      </Text>
                    </Pressable>
                  ))}
                </ScrollView>
              </View>
            )}

            {/* Description + Date row */}
            <View style={styles.inputRow}>
              <TextInput
                style={[styles.traInput, { flex: 1 }]}
                placeholder="Description"
                placeholderTextColor="#aaa"
                value={newDescription}
                onChangeText={setNewDescription}
                onFocus={() => {
                  setCurrencyDropdownVisible(false);
                  setDatePickerVisible(false);
                }}
              />
              <Pressable
                style={styles.dateButton}
                onPress={() => {
                  setDatePickerVisible(prev => !prev);
                  setCurrencyDropdownVisible(false);
                }}
              >
                <Ionicons name="calendar-outline" size={14} color="#fff" style={{ marginRight: 4 }} />
                <Text style={styles.dateButtonText}>{formatDate(selectedDate)}</Text>
              </Pressable>
            </View>

            {datePickerVisible && (
              <DateTimePicker
                value={selectedDate}
                mode="date"
                display={Platform.OS === 'ios' ? 'inline' : 'default'}
                onChange={(event, date) => {
                  if (Platform.OS === 'android') setDatePickerVisible(false);
                  if (date) setSelectedDate(date);
                }}
                maximumDate={new Date(2100, 11, 31)}
                minimumDate={new Date(2000, 0, 1)}
              />
            )}

            {/* Transaction type — 3-button row */}
            <View style={styles.typeButtonRow}>
              {/* Income */}
              <Pressable
                style={[styles.typeBtn, selectedTransactionType === 'income' && styles.typeBtnActiveIncome]}
                onPress={() => setSelectedTransactionType('income')}
              >
                <Ionicons name="caret-up" size={22} color="#22c55e" />
              </Pressable>
              {/* Expense */}
              <Pressable
                style={[styles.typeBtn, selectedTransactionType === 'expense' && styles.typeBtnActiveExpense]}
                onPress={() => setSelectedTransactionType('expense')}
              >
                <Ionicons name="caret-down" size={22} color="#ef4444" />
              </Pressable>
              {/* Subscription */}
              <Pressable
                style={[styles.typeBtn, selectedTransactionType === 'subscription' && styles.typeBtnActiveSubscription]}
                onPress={() => setSelectedTransactionType('subscription')}
              >
                <Ionicons name="refresh" size={22} color="#6495ed" />
              </Pressable>
            </View>

            <Pressable
              style={[styles.submitTraButton, isSubmitting && { opacity: 0.6 }]}
              onPress={handleAddTransaction}
              disabled={isSubmitting}
            >
              <Text style={styles.submitTraButtonText}>
                {isSubmitting ? 'Adding...' : 'Add'}
              </Text>
            </Pressable>

            <Text style={styles.pastExpensesLabel}>Past expenses</Text>
            <ScrollView style={styles.pastExpensesList} nestedScrollEnabled>
              {categoryTransactions.length === 0
                ? <Text style={styles.noExpensesText}>No expenses yet</Text>
                : categoryTransactions.map(t => (
                  <View key={t.id} style={styles.transactionRow}>
                    <View style={[
                      styles.categoryDot,
                      t.transaction_type === 'income' && { backgroundColor: '#22c55e' },
                      t.transaction_type === 'subscription' && { backgroundColor: '#6495ed' },
                    ]} />
                    <View style={{ flex: 1, marginRight: 8 }}>
                      <Text style={styles.transactionDesc}>{t.description || '—'}</Text>
                      <Text style={styles.transactionCat}>{formatDate(new Date(t.occurred_at))}</Text>
                    </View>
                    <Text style={[
                      styles.transactionAmount,
                      t.transaction_type === 'income' && { color: '#22c55e' },
                      t.transaction_type === 'subscription' && { color: '#6495ed' },
                    ]}>
                      {t.currency} {t.amount.toFixed(2)}
                    </Text>
                  </View>
                ))
              }
            </ScrollView>
          </Pressable>
        </View>
      </Modal>

      {/* ── Create Category Modal ── */}
      <Modal visible={modalCatVisible} transparent={true} onRequestClose={() => setModalCat(false)}>
        <Pressable onPress={() => setModalCat(false)} style={styles.modalCatOverlay}>
          <Pressable style={styles.modalCatContent} onPress={() => {}}>
            <Text style={styles.modalCatTitle}>New Category</Text>
            <TextInput
              style={styles.catInput}
              placeholder="Category name"
              value={newCategoryName}
              onChangeText={setNewCategoryName}
              autoFocus
            />
            <Pressable style={styles.submitCatButton} onPress={handleCreateCategory}>
              <Text style={styles.submitCatButtonText}>Create</Text>
            </Pressable>
          </Pressable>
        </Pressable>
      </Modal>

      {/* ── Add Category FAB ── */}
      <Pressable style={styles.addButton} onPress={() => setModalCat(prev => !prev)}>
        <Ionicons name="add-circle-sharp" size={60} color="#6495ed" />
      </Pressable>

    </Pressable>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },

  upperHalf: {
    height: SCREEN_HEIGHT * 0.4,
    paddingTop: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#efefef',
  },
  summaryBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginBottom: 12,
    height: 32,
  },
  summaryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  summaryIncome: {
    color: '#22c55e',
    fontWeight: '700',
    fontSize: 16,
  },
  summarySpending: {
    color: '#ef4444',
    fontWeight: '700',
    fontSize: 16,
  },
  categoryPage: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: TILE_GAP,
    alignContent: 'center',
    justifyContent: 'center',
  },
  tile: {
    width: TILE_SIZE,
    height: TILE_SIZE,
    backgroundColor: '#6495ed',
    borderRadius: 12,
    padding: 8,
    justifyContent: 'flex-end',
  },
  tilePlaceholder: {
    width: TILE_SIZE,
    height: TILE_SIZE,
  },
  tileTitle: {
    color: '#fff',
    fontWeight: '600',
    fontSize: Math.max(10, Math.floor(TILE_SIZE * 0.13)),
    marginBottom: 2,
  },
  tileAmount: {
    color: '#fff',
    fontSize: Math.max(9, Math.floor(TILE_SIZE * 0.11)),
    opacity: 0.9,
  },
  removeButton: {
    position: 'absolute',
    top: 4,
    right: 4,
  },
  dotsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 6,
    height: 28,
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: '#d1d5db',
  },
  dotActive: {
    backgroundColor: '#6495ed',
  },

  lowerHalf: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 12,
  },
  recentHeading: {
    fontSize: 15,
    fontWeight: '700',
    color: '#333',
    marginBottom: 8,
  },
  monthDivider: {
    fontSize: 12,
    fontWeight: '700',
    color: '#9ca3af',
    marginTop: 16,
    marginBottom: 4,
    letterSpacing: 0.8,
  },
  dayDivider: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6b7280',
    marginTop: 8,
    marginBottom: 4,
  },
  transactionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
    borderRadius: 10,
    padding: 10,
    marginBottom: 6,
    gap: 10,
  },
  categoryDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#ef4444',
    flexShrink: 0,
  },
  transactionDesc: {
    fontSize: 14,
    color: '#1f2937',
    fontWeight: '500',
  },
  transactionCat: {
    fontSize: 12,
    color: '#9ca3af',
    marginTop: 1,
  },
  transactionAmount: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ef4444',
  },
  noExpensesText: {
    color: '#aaa',
    textAlign: 'center',
    marginTop: 20,
  },
  seeAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 12,
    marginTop: 4,
    borderWidth: 1,
    borderColor: '#6495ed',
    borderRadius: 10,
  },
  seeAllButtonText: {
    color: '#6495ed',
    fontWeight: '600',
    fontSize: 14,
  },

  modalTraOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
    marginVertical: 20,
    marginHorizontal: 10,
  },
  modalTraContent: {
    backgroundColor: '#f2f2f2',
    padding: 24,
    borderRadius: 30,
    width: '100%',
    flex: 1,
  },
  modalTraHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTraTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#333',
  },
  closeButton: {
    padding: 4,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 10,
  },
  traInput: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#d0d0d0',
    borderRadius: 10,
    padding: 12,
    fontSize: 16,
  },
  currencyButton: {
    backgroundColor: '#6495ed',
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderRadius: 10,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    minWidth: 64,
    justifyContent: 'center',
  },
  currencyButtonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 14,
  },
  dropdown: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#d0d0d0',
    borderRadius: 10,
    marginBottom: 10,
    overflow: 'hidden',
    alignSelf: 'flex-end',
    minWidth: 100,
  },
  dropdownItem: {
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  dropdownItemSelected: {
    backgroundColor: '#e8effe',
  },
  dropdownItemText: {
    fontSize: 15,
    color: '#333',
  },
  dropdownItemTextSelected: {
    color: '#6495ed',
    fontWeight: '700',
  },
  dateButton: {
    backgroundColor: '#6495ed',
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderRadius: 10,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dateButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 13,
  },
  typeButtonRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10,
  },
  typeBtn: {
    flex: 1,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#d0d0d0',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  typeBtnActiveIncome: {
    backgroundColor: '#dcfce7',
    borderColor: '#22c55e',
  },
  typeBtnActiveExpense: {
    backgroundColor: '#fee2e2',
    borderColor: '#ef4444',
  },
  typeBtnActiveSubscription: {
    backgroundColor: '#e8effe',
    borderColor: '#6495ed',
  },
  submitTraButton: {
    backgroundColor: '#6495ed',
    padding: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 20,
    marginTop: 4,
  },
  submitTraButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  pastExpensesLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#555',
    marginBottom: 8,
  },
  pastExpensesList: {
    flex: 1,
  },

  modalCatOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalCatContent: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 10,
    width: '80%',
    gap: 12,
  },
  modalCatTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  catInput: {
    borderWidth: 1,
    borderColor: '#d0d0d0',
    borderRadius: 8,
    padding: 10,
    fontSize: 16,
  },
  submitCatButton: {
    backgroundColor: '#6495ed',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  submitCatButtonText: {
    color: '#ffffff',
    fontWeight: '600',
    fontSize: 16,
  },

  addButton: {
    position: 'absolute',
    bottom: 20,
    alignSelf: 'center',
  },
});
