export interface LeaveBalance {
  year: number;
  cl_balance: number;
  rh_balance: number;
  scl_balance: number;
  el_balance: number;
  col_balance: number;
  vl_balance: number;
}

export interface LeaveApplication {
  id: number;
  applicant_id: number;
  substitute_id: number | null;
  category: 'cl' | 'rh' | 'scl' | 'el' | 'col' | 'vl';
  start_date: string;
  end_date: string;
  is_first_half: boolean;
  is_second_half: boolean;
  purpose: string;
  station_leave: boolean;
  status: string;
  actual_resumption_date: string | null;
  deducted_days: number;
  created_at: string;
}

export interface ApplyPayload {
  category: LeaveApplication['category'];
  start_date: string;
  end_date: string;
  is_first_half?: boolean;
  is_second_half?: boolean;
  purpose: string;
  station_leave?: boolean;
  substitute_id?: number;
}