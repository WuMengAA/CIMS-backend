package service

import (
	"errors"
	"time"

	"github.com/MINIOpenSource/CIMS-backend/internal/data"
	"github.com/MINIOpenSource/CIMS-backend/internal/model"
)

var (
	ErrNotFound = errors.New("not found")
)

type ConfigService struct{}

func NewConfigService() *ConfigService {
	return &ConfigService{}
}

// -- Generic Helpers --

func (s *ConfigService) GetClientProfile(uid string) (*model.ClientProfile, error) {
	var p model.ClientProfile
	if err := data.DB.First(&p, "client_id = ?", uid).Error; err != nil {
		return nil, err
	}
	return &p, nil
}

// -- Resource Specific --

func (s *ConfigService) GetClassPlanFile(name string) (*model.CPFile, error) {
	var f model.CPFile
	if err := data.DB.First(&f, "name = ?", name).Error; err != nil {
		return nil, err
	}
	return &f, nil
}

func (s *ConfigService) SaveClassPlanFile(name, content string) error {
	var f model.CPFile
	if err := data.DB.First(&f, "name = ?", name).Error; err == nil {
		f.Content = content
		f.Version = time.Now().Unix()
		f.UpdatedAt = time.Now()
		return data.DB.Save(&f).Error
	}
	f = model.CPFile{Name: name, Content: content, Version: time.Now().Unix(), UpdatedAt: time.Now()}
	return data.DB.Create(&f).Error
}

func (s *ConfigService) GetTimeLayoutFile(name string) (*model.TLFile, error) {
	var f model.TLFile
	if err := data.DB.First(&f, "name = ?", name).Error; err != nil {
		return nil, err
	}
	return &f, nil
}

func (s *ConfigService) SaveTimeLayoutFile(name, content string) error {
	var f model.TLFile
	if err := data.DB.First(&f, "name = ?", name).Error; err == nil {
		f.Content = content
		f.Version = time.Now().Unix()
		f.UpdatedAt = time.Now()
		return data.DB.Save(&f).Error
	}
	f = model.TLFile{Name: name, Content: content, Version: time.Now().Unix(), UpdatedAt: time.Now()}
	return data.DB.Create(&f).Error
}

func (s *ConfigService) GetSubjectFile(name string) (*model.SubFile, error) {
	var f model.SubFile
	if err := data.DB.First(&f, "name = ?", name).Error; err != nil {
		return nil, err
	}
	return &f, nil
}

func (s *ConfigService) SaveSubjectFile(name, content string) error {
	var f model.SubFile
	if err := data.DB.First(&f, "name = ?", name).Error; err == nil {
		f.Content = content
		f.Version = time.Now().Unix()
		f.UpdatedAt = time.Now()
		return data.DB.Save(&f).Error
	}
	f = model.SubFile{Name: name, Content: content, Version: time.Now().Unix(), UpdatedAt: time.Now()}
	return data.DB.Create(&f).Error
}

func (s *ConfigService) GetPolicyFile(name string) (*model.PolicyFile, error) {
	var f model.PolicyFile
	if err := data.DB.First(&f, "name = ?", name).Error; err != nil {
		return nil, err
	}
	return &f, nil
}

func (s *ConfigService) SavePolicyFile(name, content string) error {
	var f model.PolicyFile
	if err := data.DB.First(&f, "name = ?", name).Error; err == nil {
		f.Content = content
		f.Version = time.Now().Unix()
		f.UpdatedAt = time.Now()
		return data.DB.Save(&f).Error
	}
	f = model.PolicyFile{Name: name, Content: content, Version: time.Now().Unix(), UpdatedAt: time.Now()}
	return data.DB.Create(&f).Error
}

func (s *ConfigService) GetSettingsFile(name string) (*model.SettingsFile, error) {
	var f model.SettingsFile
	if err := data.DB.First(&f, "name = ?", name).Error; err != nil {
		return nil, err
	}
	return &f, nil
}

func (s *ConfigService) SaveSettingsFile(name, content string) error {
	var f model.SettingsFile
	if err := data.DB.First(&f, "name = ?", name).Error; err == nil {
		f.Content = content
		f.Version = time.Now().Unix()
		f.UpdatedAt = time.Now()
		return data.DB.Save(&f).Error
	}
	f = model.SettingsFile{Name: name, Content: content, Version: time.Now().Unix(), UpdatedAt: time.Now()}
	return data.DB.Create(&f).Error
}

// Helper for Mgmt API list
func (s *ConfigService) ListFiles(resourceType string) ([]string, error) {
	var names []string
	switch resourceType {
	case "ClassPlan":
		data.DB.Model(&model.CPFile{}).Pluck("name", &names)
	case "TimeLayout":
		data.DB.Model(&model.TLFile{}).Pluck("name", &names)
	case "Subjects":
		data.DB.Model(&model.SubFile{}).Pluck("name", &names)
	case "Policy":
		data.DB.Model(&model.PolicyFile{}).Pluck("name", &names)
	case "DefaultSettings":
		data.DB.Model(&model.SettingsFile{}).Pluck("name", &names)
	default:
		return nil, errors.New("unknown resource type")
	}
	return names, nil
}

// Helper for Mgmt API delete
func (s *ConfigService) DeleteFile(resourceType, name string) error {
	switch resourceType {
	case "ClassPlan":
		return data.DB.Delete(&model.CPFile{}, "name = ?", name).Error
	case "TimeLayout":
		return data.DB.Delete(&model.TLFile{}, "name = ?", name).Error
	case "Subjects":
		return data.DB.Delete(&model.SubFile{}, "name = ?", name).Error
	case "Policy":
		return data.DB.Delete(&model.PolicyFile{}, "name = ?", name).Error
	case "DefaultSettings":
		return data.DB.Delete(&model.SettingsFile{}, "name = ?", name).Error
	default:
		return errors.New("unknown resource type")
	}
}
